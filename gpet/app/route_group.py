import asyncio
import uuid
import math
import ujson
import datetime

from sanic.log import logger
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import inject_user

from app import db, redis
from app.send_message import send_text_msg, send_image_msg
from app.route_requests import update_robot_nickname, cancel_group, activate_group, sync_group_members
from app.common import check_robot_amount_distribute, currency_delete_group, get_user_by_code, get_robot_by_code, \
    remove_robot_distribute, get_robot_by_id, get_group_info
from ut.constants import RESOURCE_NOT_FOUND_CODE, SERVICE_SUCCESS_CODE, SENSITIVE_WORD_CODE, EXTERNAL_INTERFACE_CODE
from ut.constants import SNAPSHOT_KEY_REDIS_KEY, DISTRIBUTE_KEY_REDIS_KEY, \
    GROUP_USER_ROBOT_MAP_REDIS_KEY, ACTIVATED_KEY_REDIS_KEY, GROUP_WELCOME_MSG_RECORD_REDIS_KEY, \
    STATISTICS_USER_GROUPS_REDIS_KEY, GroupCancelReason
from ut.response import response_json
from config import settings
from ut.utils import records_to_list, get_page_info, aly_text_check, today

LOCALHOST = settings['LOCALHOST']
GROUP_LIST_URL = ''.join([LOCALHOST, '/grouppet/group?userId={user_id}'])

DISTRIBUTE_COUNT = settings['DISTRIBUTE_CONFIG']
DISPLAY_RATE = settings['DISPLAY_RATE']
REDIS_EXPIRE_TIME = 2 * 24 * 3600
NEW_ROBOT_WORD = '主人，我今天体力消耗完了，暂时不能入群。请您扫码加我的小伙伴【{robot_name}】进群【{group_name}】，为主人继续赚钱！'
NO_ROBOT_WORD = '主人，我今天体力消耗完了，现在也没有其他训练好的小宠物，请主人等到明天再拉我进群赚钱吧'
DISTRIBUTE_NEW_ROBOT = "小宠物今天进群额度已满，主人可以加下方的【{robot_name}】为好友，拉它入群同样可以帮主人赚票票～"
GROUP_HAS_OPEN_BY_OTHER = "【{group_name}】已经被其他主人占领啦，请把我拉进其他群吧！"
GROUP_ROBOT_CALL_BACK_WORD = '主人，我被从【{group_name}】中踢出来啦，快把我拉回去吧[Sob]'
GROUP_QUALITY_LOWER = '[撇嘴] 诶呀，这个群小宠之前进过呢。\n里面的群友都不看小宠的文章，\n小宠一点都不开心！主人换个群吧'
GROUP_INVOLVES_YELLOW_GAMBLING = '😱 糟糕\n【{groupname}】涉嫌破坏微信生态，小宠先退群啦，\n主人请爱惜我，拉我进更好的群好不好～'
GROUP_WAIT_STAR_RATE = '------🎉入住成功🎉------\n\n群名：【{group_name}】\n[Packet]小宠正在体验群内舒适度，拉群红包预计1-2天后送达。\n[Smart]体验期间，群内@小宠还可与小宠互动哦\n\n回复【菜单】查看小宠更多功能'
robot_threshold_spend_out = '【{group_name}】开通失败，请将邀请撤回'

group_status = {
    "normal": 1,
    "error": 0
}

group_income = {
    1: 0.6,
    2: 1.5,
    3: 3,
    4: 9,
    5: 30
}
click_income = 0.16

group_running_status = {
    1: "正常",
    2: "已被踢",
}


async def robot_into_group_callback(data):
    """
   待开通群回调
    :param data:
    :return:
    """
    group_code = data.get('group_id', None)
    robot_code = data.get('robot_id', None)
    user_code = data.get('user_id', None)
    group_name = data.get('name', '未命名')
    logger.info(f'robot into group callback, robot_code:{robot_code}, group_code:{group_code},mem_code:{user_code}')

    user_info = await get_user_by_code(user_code)
    user_id = str(user_info['id']) if user_info is not None else None
    is_block = user_info['status'] if user_info is not None else None
    if user_id is None or is_block == 2:
        logger.info('user is not exist or user haven been blocked')
        return
    lock_value = await acquire_lock_group(group_code, release_time=30)
    logger.info(f'set lock to group {group_code} and  if group lock success:[{lock_value}]')
    if not lock_value:
        return
    robot_info = await get_robot_by_code(robot_code)
    if robot_info is None:
        return
    robot_id = str(robot_info['id'])
    count_distribute = robot_info['count_distribute']
    if not await check_robot_distribute_count(robot_id, count_distribute, user_id, user_code, robot_code, group_name,
                                              user_info['channel']):
        return
    if await group_delete_history(group_code, robot_code, user_code, group_name):
        return
    if await check_group_activated(group_code, robot_code, user_code, group_name):
        return
    await request_bind_group(group_code, robot_code, robot_id, user_id, user_code, user_info['channel'], group_name)
    return


async def check_robot_distribute_count(robot_id, count_distribute, user_id, user_code, robot_code, group_name, channel):
    result = True
    if count_distribute >= 30:
        result = False
        await remove_robot_distribute(robot_id)
        distribute = await distribute_now_robot(user_id, user_code, channel)
        if distribute is not None:
            send_msg = NEW_ROBOT_WORD.format(robot_name=distribute[0], group_name=group_name)
            await send_text_msg(robot_code, user_code, robot_threshold_spend_out.format(group_name=group_name))
            await asyncio.sleep(0.05)
            await send_text_msg(robot_code, user_code, send_msg)
            await asyncio.sleep(0.05)
            await send_image_msg(robot_code, user_code, distribute[1])
    return result


async def request_bind_group(group_code, robot_code, robot_id, user_id, user_code, channel, group_name):
    activate_result = await activate_group({"group_id": group_code, "robot_id": robot_code})
    logger.info(f'request gbot to activate group:group_code=[{group_code}], robot_code=[{robot_code}] '
                f'and result is[{activate_result}] ')
    if activate_result and int(activate_result['code']) == 100:
        return
    else:
        logger.error(f'request gbot to activate group:[{group_code}] failed')
        await remove_robot_distribute(robot_id)
        result = await distribute_now_robot(user_id, user_code, channel)
        if result is not None:
            send_msg = NEW_ROBOT_WORD.format(robot_name=result[0], group_name=group_name)
            await send_text_msg(robot_code, user_code, send_msg)
            await asyncio.sleep(0.05)
            await send_image_msg(robot_code, user_code, result[1])


async def acquire_lock_group(lock_name, release_time=30):
    """
    获取锁
    :param lock_name: 锁名称
    :param release_time: 尝试获取锁时间
    :return: 获取锁失败返回False
    """
    identifier = str(uuid.uuid4())
    lock_name = 'lock:' + lock_name
    lock_timeout = int(math.ceil(release_time))
    if await redis.conn.set(lock_name, identifier, nx=True, ex=lock_timeout):
        return True
    return False


async def check_group_activated(group_code, robot_code, mem_code, name):
    """根据群code查询该群是否被激活"""
    result = False
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
            select robot_group_map.robot_id::varchar, "group".code, "group".user_id::varchar, "group".id::varchar,
            "group".owner_user_code,robot.code as robot_code, "group".name, "group".running_status from "group" 
            join robot_group_map  on "group".id = robot_group_map.group_id join "robot" on 
            robot.id=robot_group_map.robot_id where "group".code=$1 and "group".status<>3 
            and "robot_group_map".status <>3 and "robot".status<>3''')
        val = await select_stmt.fetchrow(group_code)
    if val is not None:
        await send_text_msg(robot_code, mem_code, GROUP_HAS_OPEN_BY_OTHER.format(group_name=name))
        result = True
    return result


async def checkout_user_has_group(user_id):
    """判断用户是否首次导群, 是，记录用户一导群"""
    async with db.conn.acquire() as con:
        get_user_stmt = await con.prepare('''select count(1) from  "group" where user_id = $1''')
        count = await get_user_stmt.fetchval(user_id)
    if count <= 1:
        await record_user_first_activate_group(user_id)


async def record_user_first_activate_group(user_id):
    """记录用户首次导群"""
    async with db.conn.acquire() as con:
        update_user = await con.prepare('''
        update "user" set need_remind = jsonb_set(need_remind, $1, $2::jsonb), update_date = now() where id = $3''')
        await update_user.fetch({"is_import"}, '1', user_id)


async def group_delete_history(group_code, robot_code, user_code, group_name):
    """根据群code 查询该群以前是否在注销过"""
    result = False
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
            select  code, cancel_reason from "group" where code=$1  and status=3 order by create_date desc ''')
        group_has_delete = await select_stmt.fetchrow(group_code)
    if group_has_delete is not None:
        if group_has_delete['cancel_reason'] == GroupCancelReason.ILLEGAL:
            content = GROUP_INVOLVES_YELLOW_GAMBLING.format(group_name=group_name)
            await send_text_msg(robot_code, user_code, content)
            result = True
        elif group_has_delete['cancel_reason'] == GroupCancelReason.LAUNCH_LOW:
            content = GROUP_QUALITY_LOWER.format(group_name=group_name)
            await send_text_msg(robot_code, user_code, content)
            result = True
    return result


async def add_group_record(group_code, name, user_id, robot_id):
    """导群成功记录群，机器人相关数据"""
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select  settle_count from "group" where code=$1 order by create_date desc''')
        group_has_delete = await select_stmt.fetchval(group_code)
    settle_count = group_has_delete if group_has_delete is not None else 0
    status = 2 if settle_count >= 30 else 1
    template_info = await get_group_profit_template()
    async with db.conn.acquire() as con:
        async with con.transaction():
            it = await con.prepare(
                '''insert into "group" (id, code,name, user_id, settle_count, status, profit_template_id, tuling_switch)
                   values (uuid_generate_v4(), $1, $2, $3, $4, $5, $6, $7) returning id::varchar''')
            group_id = await it.fetchval(group_code, name, user_id, settle_count, status, template_info['id'], 1)

            insert_map_stmt = await con.prepare('''
            insert into "robot_group_map" (id, robot_id, group_id, status) values (uuid_generate_v4(), $1, $2, 1) ''')
            await insert_map_stmt.fetch(robot_id, group_id)

            update_stmt = await con.prepare('''
                update "robot" set count_distribute=count_distribute+1, update_date = now() where id=$1 ''')
            await update_stmt.fetch(robot_id)
    return group_id


async def get_group_profit_template():
    """查询群的结算模版"""
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
            select id, code from "group_profit_template" where start_date<=now() and end_date>=now() and 
            code<>'DEFAULT' and status<>3 union all select id, code from "group_profit_template" where 
            code='DEFAULT' and not exists (select id, code from "group_profit_template" where start_date<=now() and 
            end_date>=now() and code<>'DEFAULT' and status<>3) ''')
        template_info = await select_stmt.fetchrow()
        return template_info


async def group_activated_callback(data):
    """
    1. 判断是否群宠用户和是否封号
        * 不是群宠用户 或被封号 注销由创群
        * 是群宠用户并且没有被封号 执行步骤2
    2. 该群是否被激活（status!= 3）
        * 激活，激活群失败，发私聊消息
        * 没有被激活，执行步骤3
    3. 该群是否以前被激活，
        * 获取结算天数 执行步骤4
    4. 插入group记录，map记录 更新robot表机器人激活额度（事务）
    5. redis记录机器人当日激活群数，并判断该机器人的额度是否到达当日最大的额度
        * 是 删除机器人快照缓存
    6. 判断该用户是否是首次导群
        * 是 修改user 表是否导群记录
    7. 给用户发送群激活成功的私聊消息
    8. 调用分配机器人接口，传入激活群机器人，以及要分配的额度，获取一个机器人
        * 返回机器人是当前机器人 不做操作
        * 返回机器人不是当前机器人 给用户发送私聊消息，推送机器人二维码

    :param :
    :return:
    """
    group_code = data.get('group_id')
    robot_code = data.get('robot_id')
    mem_code = data.get('user_id')
    name = data.get('name', '未命名')
    logger.info(f'robot activated group callback, robot_code:{robot_code}, group_code:{group_code},mem_code:{mem_code}')
    # 1
    user_info = await get_user_by_code(mem_code)
    if user_info is None or user_info['status'] == 2:
        await cancel_group(data)
        logger.debug('user is not exist')
        return
    user_id = str(user_info['id'])
    channel = user_info['channel']
    robot_info = await get_robot_by_code(robot_code)
    robot_id = str(robot_info['id'])
    # 2
    key = 'bind_group:' + group_code
    if not await acquire_lock_group(key, release_time=30):
        return
    if await check_group_activated(group_code, robot_code, mem_code, name):
        return
    group_id = await add_group_record(group_code, name, user_id, robot_id)
    logger.info(f'activate group [{group_code}] for user [{mem_code}]')
    redis_val = {"group_code": group_code, "user_id": user_id, "user_code": mem_code,
                 "robot_id": robot_id, "robot_code": robot_code, "group_id": group_id}
    await redis.conn.hset(GROUP_USER_ROBOT_MAP_REDIS_KEY, group_code, ujson.dumps(redis_val))
    # 发起同步群成员
    await update_cache_after_bind_group(robot_id)
    await sync_group_members({"group_id": group_code})
    # 判断用户是否是首次导群
    await checkout_user_has_group(user_id)
    await send_text_msg(robot_code, mem_code, GROUP_WAIT_STAR_RATE.format(group_name=name))

    result, distribute_robot_id = await check_robot_amount_distribute(user_id, mem_code, channel, robot_code)
    if distribute_robot_id is not None:
        if distribute_robot_id != robot_id:
            robot = await get_robot_by_id(distribute_robot_id)
            robot_name = robot.get('name')
            qr_code = robot.get('qr_code')
            send_msg = DISTRIBUTE_NEW_ROBOT.format(robot_name=robot_name)
            await send_text_msg(robot_code, mem_code, send_msg)
            await send_image_msg(robot_code, mem_code, qr_code)
    else:
        logger.warning(f'request [robot_distribution] to distribute robot result is None')
        await send_text_msg(robot_code, mem_code, NO_ROBOT_WORD)
    return


async def update_cache_after_bind_group(robot_id):
    key = ACTIVATED_KEY_REDIS_KEY.format(today=today())
    key_exists = await redis.conn.exists(key)
    if not key_exists:
        activate_count = await redis.conn.zadd(key, **{robot_id: 1})
        await redis.conn.expire(key, REDIS_EXPIRE_TIME)
    else:
        activate_count = await redis.conn.zincrby(key, robot_id, 1)

    max_time_key = SNAPSHOT_KEY_REDIS_KEY.format(today=today())
    max_time = await redis.conn.zscore(max_time_key, robot_id)

    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    count = 0
    if max_time:
        count = int(max_time / DISPLAY_RATE - activate_count)
    if count <= 0:
        await remove_robot_distribute(robot_id)
    else:
        if await redis.conn.zscore(distribute_key, robot_id):
            await redis.conn.zadd(distribute_key, **{robot_id: count})


async def distribute_now_robot(user_id, user_code, channel, robot_code=None):
    result, distribute_robot_id = await check_robot_amount_distribute(user_id, user_code, channel, robot_code)
    if not result and distribute_robot_id:
        robot = await get_robot_by_id(distribute_robot_id)
        robot_name = robot.get('name')
        qr_code = robot.get('qr_code')
        return robot_name, qr_code
    elif not distribute_robot_id:
        logger.warning(f'request [robot_distribution] to distribute robot result is None')
        await send_text_msg(robot_code, user_code, NO_ROBOT_WORD)
        return None


# @bp.route('/groups')
@protected()
@inject_user()
async def get_group_list(request, user, **kwargs):
    """获取用户的群列表"""
    user_id = user.get('user_id')
    status = request.raw_args.get('status')
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    user_groups = []
    total_records = 0
    async with db.conn.acquire() as con:
        if int(status) == group_status['normal']:
            select_stmt = await con.prepare('''
            select "group".code, "group".launch_switch, "group".settle_count, "group".quality_level, "group".old_group,
            robot_group_map.nickname,"group".name , "robot".name as robot_name from "group" left join robot_group_map on
             "group".id = "robot_group_map".group_id left join robot on robot.id = "robot_group_map".robot_id where 
             "group".user_id = $1 and "group".status<>3 and "robot_group_map".status <>3 and "robot".status<>3 and 
             (quality_level is not null or old_group = 1) order by "group".create_date desc limit $2 offset $3''')
            user_groups = records_to_list(
                await select_stmt.fetch(user_id, int(page_size), int(current_page) * int(page_size)))

            select_count = await con.prepare('''select count(1) from "group" left join robot_group_map on 
            "group".id = robot_group_map.group_id left join robot on robot.id = robot_group_map.robot_id
                where "group".user_id = $1 and "group".status<>3 and "robot_group_map".status <>3 and "robot".status<>3 
                and (quality_level is not null or old_group = 1)''')
            total_records = await select_count.fetchval(user_id)
        elif int(status) == group_status['error']:
            select_stmt = await con.prepare(''' 
            select "group".code , "group".name, to_char("group".create_date, 'YYYY-MM-DD') as create_date  from "group"  where "group".user_id = $1 and "group".status != 3 and old_group != 1
            and quality_level is null order by "group".create_date desc limit $2 offset $3''')
            user_groups = records_to_list(
                await select_stmt.fetch(user_id, int(page_size), int(current_page) * int(page_size)))

            select_count = await con.prepare('''select count(1) from "group" 
                where user_id = $1 and status != 3  and quality_level is null and old_group != 1''')
            total_records = await select_count.fetchval(user_id)

    page_info = get_page_info(page_size, current_page, total_records)
    if len(user_groups) > 0 and int(status) == group_status['normal']:
        for item in user_groups:
            if not item['old_group']:
                if item['settle_count'] >= 30 and item['launch_switch'] == 0:
                    income_status = '未收益'
                else:
                    income_status = '收益中'
                item['income_status'] = income_status
                item['group_income'] = group_income[item['quality_level']]
            item['text_income'] = click_income
            item['robot_name'] = item['nickname'] if item['nickname'] else item['robot_name']
            item.pop('nickname')
    return response_json(user_groups, page_info=page_info)


# @bp.route('/groups/<group_code:[a-z-A-Z-0-9\\-]+>/robot_name', methods=['PUT'])
@protected()
@inject_user()
async def modify_robot_nickname(request, user, group_code):
    """修改群内机器人的昵称"""
    user_id = user.get('user_id')
    remark_name = request.json.get('remark_name')
    logger.debug(f'modify_robot_name, group_id:{group_code}, remark_name:{remark_name}')
    if not await aly_text_check(remark_name):
        return response_json(None, SENSITIVE_WORD_CODE, msg='修改内容涉及敏感词')
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
        select "group".id, "group".code, robot.code as robot_code from "group" left join robot_group_map 
        on "group".id=robot_group_map.group_id left join robot on robot.id=robot_group_map.robot_id 
        where "group".code=$1 and "group".user_id= $2 and "group".status<>3 and "robot_group_map".status<>3 
        and "robot".status<>3''')
        group_info = await select_stmt.fetchrow(group_code, user_id)

    data = {"group_id": group_info['code'],
            "robot_id": group_info['robot_code'],
            "nickname": remark_name}
    result = await update_robot_nickname(data)
    logger.info(result)
    if int(result['code']) == 100:
        async with db.conn.acquire() as con:
            update_stmt = await con.prepare('''
            update robot_group_map set nickname=$1, update_date = now() where group_id=$2''')
            await update_stmt.fetch(remark_name, group_info['id'])
        return response_json(None, code=SERVICE_SUCCESS_CODE, msg='修改成功')
    else:
        return response_json(None, code=EXTERNAL_INTERFACE_CODE, msg='修改失败')


# @bp.route('/groups/statistics')
@protected()
@inject_user()
async def group_statistic(request, user):
    user_id = user.get('user_id')
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    user_groups, page_info = await user_owner_group_info(user_id, page_size, current_page)
    if user_groups is None:
        logger.debug('user has no group')
        return response_json(None)
    user_group_list = []
    # 获取该用户昨日去群退群，及发言人数
    date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    statistic_user_groups = STATISTICS_USER_GROUPS_REDIS_KEY.format(today=date)
    statistic_user_groups_record = await redis.conn.hget(statistic_user_groups, user_id)
    if statistic_user_groups_record is None:
        statistic_user_groups_record = '{}'
    statistic_user_groups_record = ujson.loads(statistic_user_groups_record)

    for group in user_groups:
        group_static_record = statistic_user_groups_record.get(group['code'], {})
        group_dict = {
            'group_id': group['id'],
            'group_name': group['name'],
            'group_mem_counts': group['mem_count'] if group['mem_count'] is not None else 0,
            'join_group_counts': group_static_record.get('join_group', 0),
            'exit_group_counts': group_static_record.get('retreat_group', 0),
            'speaker_counts': group_static_record.get('msg_counts', 0),
        }
        user_group_list.append(group_dict)
    logger.debug(user_group_list)
    return response_json(user_group_list, page_info=page_info)


async def user_owner_group_info(user_id, page_size, current_page):
    """查询用户群主群信息"""
    async with db.conn.acquire() as con:
        if page_size == -1:
            st = await con.prepare('''
            select "group".id::varchar , "group".code, "group".name, launch_switch,mem_count, welcome_msg,
            to_char("group".create_date, 'YYYY-MM-DD HH24:MI:SS') as create_date from "group" left join "user" on 
            "group".user_id = "user".id where user_id = $1 and "group".owner_user_code = "user".code 
            and "group".status !=3 order by create_date desc''')
            groups = records_to_list(await st.fetch(user_id))
        else:
            st = await con.prepare('''
            select "group".id::varchar , "group".code, "group".name,mem_count, welcome_msg, launch_switch,
            to_char("group".create_date, 'YYYY-MM-DD HH24:MI:SS') as create_date from "group" left join "user" on 
            "group".user_id = "user".id where user_id = $1 and owner_user_code = "user".code and "group".status !=3 
            order by create_date desc limit $2 offset $3''')
            groups = records_to_list(await st.fetch(user_id, int(page_size), int(current_page)*int(page_size)))
        select_count = await con.prepare('''select count(1) from "group" left join "user" on "group".user_id="user".id
        where user_id = $1 and owner_user_code ="user".code and "group".status !=3''')
        total_records = await select_count.fetchval(user_id)
        page_info = get_page_info(page_size, current_page, total_records)
    return groups, page_info


# @bp.route('/groups/<group_id:[a-z-A-Z-0-9\\-]+>/welcome', methods=['POST'])
@protected()
@inject_user()
async def update_group_welcome_msg(request, user, group_id):
    """设置群欢迎语"""
    welcome_msg = request.json.get('welcome_msg')
    if not await aly_text_check(welcome_msg):
        return response_json(None, SENSITIVE_WORD_CODE, msg='内容涉及敏感词')
    async with db.conn.acquire() as con:
        update_stmt = await con.prepare('''update "group" set welcome_msg=$1, update_date = now() where id=$2 ''')
        await update_stmt.fetch(welcome_msg, group_id)
    return response_json(None)


# @bp.route('/groups/welcome')
@protected()
@inject_user()
async def group_welcome_msg(request, user):
    """查询用户群欢迎语"""
    user_id = user.get('user_id')
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    user_groups, page_info = await user_owner_group_info(user_id, page_size, current_page)
    user_groups = [pop_dict_keys(item, ['launch_switch', 'code', 'create_date', 'mem_count']) for item in user_groups]
    return response_json(user_groups, page_info=page_info)


async def member_into_group_callback(data):
    """群成员入群回调"""
    '''{
    "group_id": "20181111222222",
    "user_id": "20181111222222",
    "invite_user_id": "20181111222222",
    "nickname": "群成员",
    "avatar": "http://xxx/xxx.png",
    "user_wxid": "wxid_xxxxxxxx",
    "join_type": 0,
    "join_time": "1970-01-01T00:00:00"
 }'''
    # 用户ID，邀请人ID，群ID，入群时间
    group_code = data.get('group_id')
    logger.debug(f'new member join group, data:{data}')

    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
        select  "group".code,"group".id, "group".user_id, robot.code as robot_code,"group".welcome_msg from "group" 
        join robot_group_map  ON "group".id = robot_group_map.group_id join robot on robot_group_map.robot_id=robot.id
        where "group".code=$1 AND "group".status<>3 and "robot_group_map".status <>3 and "robot".status<>3 ''')
        group_info = await select_stmt.fetchrow(group_code)
    if not group_info:
        logger.error(f'member_into_group_callback: not match group: {group_code}')
        return
    user_id = group_info['user_id']
    group_id = group_info['id']
    robot_code = group_info['robot_code']
    welcome_msg = group_info['welcome_msg']
    await update_join_and_retreat_redis_record(user_id, group_code, 'join_group')

    # 触发入群欢迎语
    logger.debug(f'{group_id} welcome_msg is {welcome_msg}')
    if welcome_msg is not None:
        welcome_key = GROUP_WELCOME_MSG_RECORD_REDIS_KEY + ":{}".format(group_id)
        has_record = await redis.conn.exists(welcome_key)
        if not has_record:
            await send_text_msg(robot_code, [data['user_id']], welcome_msg, group_code)
            await redis.conn.setex(welcome_key, 300, 1)


async def member_retreat_group_callback(data):
    """群成员退群回调"""
    # 用户ID，群ID，退群时间
    group_code = data.get('group_id')
    logger.debug(f'new member retreat group, group_code:{group_code}')
    group_info = await get_group_info(group_code)
    if not group_info:
        logger.error(f'member_retreat_group_callback: not match group: {group_code}')
        return
    user_id = group_info['user_id']
    await update_join_and_retreat_redis_record(user_id, group_code, 'retreat_group')


async def update_join_and_retreat_redis_record(user_id, group_code, record_type):
    """更新群成员入群或退群redis记录"""
    key = STATISTICS_USER_GROUPS_REDIS_KEY.format(today=today())
    user_group_member_statistic = await redis.conn.hget(key, user_id)
    if user_group_member_statistic is None:
        value = {group_code: {record_type: 1}}
    else:
        val = user_group_member_statistic
        value = ujson.loads(val)
        if group_code in value:
            if record_type not in value[group_code]:
                value[group_code][record_type] = 1
            else:
                value[group_code][record_type] = value[group_code][record_type] + 1
        else:
            value[group_code] = {record_type: 1}
    await redis.conn.hset(key, user_id, ujson.dumps(value))
    await redis.conn.expire(key, REDIS_EXPIRE_TIME)


# @bp.route('/owner/group/verify')
@protected()
@inject_user()
async def owner_group_verify(request, *args, **kwargs):
    """判断用户是否有群主群"""
    user_id = kwargs['user']['user_id']
    async with db.conn.acquire() as con:
        select_owner_group = await con.prepare(
            '''select count(1) from "group"  left join "user" on "group".user_id = "user".id where 
               user_id = $1 and owner_user_code = "user".code and "group".status <> 3''')
        group = await select_owner_group.fetchval(user_id)
        if group == 0:
            return response_json(False, msg='没有群主群')
        else:
            return response_json(True)


# @bp.route('/owner/groups')
@protected()
@inject_user()
async def get_owner_group(request, *args, **kwargs):
    '''获取用户的群主群列表'''
    user_id = kwargs['user']['user_id']
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    user_groups, page_info = await user_owner_group_info(user_id, page_size, current_page)
    user_groups = [pop_dict_keys(item, ['mem_count', 'welcome_msg']) for item in user_groups]
    return response_json(user_groups, page_info=page_info)


def pop_dict_keys(item, key_list):
    for key in key_list:
        item.pop(key)
    return item


# @bp.route('/groups/delete', methods=['POST'])
async def delete_groups(request):
    group_ids = request.json.get('group_ids')
    logger.info(f'delete group len: {len(group_ids)}')
    cancel_reason = request.raw_args.get('cancel_reason', GroupCancelReason.SYSTEM_ACTIVE)
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(delete_group_task(group_ids, cancel_reason), loop)
    return response_json(None)


async def inner_delete_groups(group_ids, cancel_reason=GroupCancelReason.SYSTEM_ACTIVE):
    """系统内部方法删除群"""
    if not group_ids:
        return
    logger.info(f'inner delete group len: {len(group_ids)}')
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(delete_group_task(group_ids, cancel_reason), loop)


async def delete_group_task(group_ids, cancel_reason):
    for index in range(0, len(group_ids), 300):
        tasks = []
        items = group_ids[index: index + 300]
        for group_id in items:
            tasks.append(currency_delete_group(group_id, cancel_reason))
        await asyncio.gather(*tasks)
    logger.info(f'delete group end')


# @bp.route('/group/<group_id:[a-zA-Z0-9\\-]+>', methods=['DELETE'])
@protected()
@inject_user()
async def delete_group(request, group_id, user):
    user_id = user.get('user_id')
    cancel_reason = request.raw_args.get('cancel_reason', GroupCancelReason.SYSTEM_ACTIVE)
    """删除群"""
    if await currency_delete_group(group_id, cancel_reason):
        return response_json(True)
    else:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='group not exist!')


# @bp.route('/pullback/<group_id:[a-zA-Z0-9\\-]+>', methods=['GET'])
@protected()
@inject_user()
async def exception_group_pull(request, user, group_id):
    '''异常群拉回'''
    user_id = user.get('user_id')
    async with db.conn.acquire() as con:
        get_robot_stmt = await con.prepare(
            '''select "robot".code, "robot".qr_code from "robot_group_map" 
               left join "robot" on "robot_group_map".robot_id = "robot".id where "robot_group_map".group_id = $1 and 
               "robot_group_map".status <> 3''')
        get_group_stmt = await con.prepare('''select name from "group" where id = $1 limit 1''')
        get_user_stmt = await con.prepare('''select code from "user" where id = $1 limit 1''')
        robot = await get_robot_stmt.fetchrow(group_id)
        robot_code = robot.get('code')
        qr_code = robot.get('qr_code')
        user_code = await get_user_stmt.fetchval(user_id)
        group_name = await get_group_stmt.fetchval(group_id)
        content = GROUP_ROBOT_CALL_BACK_WORD.format(group_name=group_name)
        await send_text_msg(robot_code, user_code, content=content)
    return response_json(qr_code)


async def group_sync(group_info):
    logger.debug(f'group sync, group_info:{group_info}')
    group_code = group_info.get('id')
    group_name = group_info.get('name')
    admin_user_id = group_info.get('admin_user_id')
    mem_count = group_info.get('mem_count')
    robots = group_info.get('robots')
    if robots:
        if robots[0].get('robot_in_group'):
            robot_in_group = 1
        else:
            robot_in_group = 2
    else:
        robot_in_group = 2
    async with db.conn.acquire() as con:
        if robot_in_group == 2:
            get_group_stmt = await con.prepare('''select id::varchar from "group" where code = $1 and status <> 3''')
            group_id = await get_group_stmt.fetchval(group_code)
            await currency_delete_group(group_id, GroupCancelReason.ROBOT_KICKED)  # 机器人退群
            return
        else:
            update_group_stmt = await con.prepare('''
            update "group" set name = $1, owner_user_code = $2, mem_count = $3, running_status = $4,
                 update_date = now() where code = $5 and status <> 3''')
            await update_group_stmt.fetch(group_name, admin_user_id, mem_count, robot_in_group, group_code)


async def unbind_group(data):
    """解绑群回调"""
    robot_code = data.get('robot_id')
    group_code = data.get('group_id')
    cancel_reason = int(data.get('reason'))
    async with db.conn.acquire() as con:
        async with con.transaction():
            get_group_stmt = await con.prepare('''select id from "group" where code = $1 and status <> 3''')
            group_id = await get_group_stmt.fetchval(group_code)
            if group_id is None:
                return
            update_group = await con.prepare('''
                update "group" set status = 3, cancel_reason = $1, update_date = now() 
                where code = $2 and status <> 3''')
            await update_group.fetchrow(cancel_reason, group_code)
            update_robot_map = await con.prepare('''update robot_group_map set status = 3, update_date = now() 
                    where group_id = $1''')
            await update_robot_map.fetchrow(group_id)
            update_robot = await con.prepare('''update robot set count_distribute = count_distribute - 1, update_date = now() 
                    where code = $1''')
            await update_robot.fetchrow(robot_code)
    await redis.conn.hdel(GROUP_USER_ROBOT_MAP_REDIS_KEY, group_code)
