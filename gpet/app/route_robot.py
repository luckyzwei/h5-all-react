import ujson
from itertools import groupby
from operator import itemgetter

from sanic.log import logger

from config import settings
from app import db, redis
from app.send_message import send_text_msg, send_image_msg
from app.route_shorten import long_to_short
from app.common import check_robot_amount_distribute, currency_delete_group, remove_robot_distribute, \
    robot_distribution, update_user_income
from ut.constants import PARAMS_ERROR_CODE, ROBOT_NOT_ENOUGH_CODE, SNAPSHOT_KEY_REDIS_KEY, \
    DISPLAY_KEY_REDIS_KEY, USER_ACCOUNT_REDIS_KEY, ROBOT_BLOCKED_REDIS_KEY, GPET_ROBOT_ADD_FRIEND_REDIS_KEY,\
    GroupCancelReason
from ut.utils import records_to_list, today, set_lock
from ut.response import response_json, dumps

DISTRIBUTE_AMOUNT = settings['DISTRIBUTE_AMOUNT']
DISTRIBUTE_CONFIG = settings['DISTRIBUTE_CONFIG']
DISPLAY_RATE = settings['DISPLAY_RATE']     # 机器人展示比率

KEY_TIMEOUT = 2 * 24 * 3600
CREATE_STATUS = 1


# 推荐新机器人话术
NEW_ROBOT_WORD = '主人，我今天体力消耗完了，暂时不能入群。请您扫码加我的小伙伴【{robot_name}】进群【{group_name}】，为主人继续赚钱！'
# 没有新机器人话术
NO_ROBOT_WORD = '主人，我今天体力消耗完了，现在也没有其他训练好的小宠物，请主人等到明天再拉我进群赚钱吧！'
# 是否需要提醒jsonb
NEED_REMIND_JSON = {"is_import": 0, "is_apprentice": 0, "remind": 1}
# 用户补全信息链接
COMPLETE_LINK = '{host}/grouppet/home?userId={user_id}'
# 新注册用户指引
GIF_LINK = 'https://cloud.gemii.cc/lizcloud/fs/noauth/media/5c10e151519b3f001793e02c'
# 加好友发送话术
ADD_FRIEND_WORD = '[Hey]Hi，主人:\n我是微信群智能微小宠。\n初次见面，送你新人大红包[Packet]，点击{home_url}立即领取~'
# 加封号机器人为好友
ADD_BLOCKED_ROBOT_WORD = '终于等到你啦，主人！请把我拉进{group_names}, 这样我就可以继续在群内帮您赚钱啦！'
# 机器人领养费用
ROBOT_ADD_COST = 0.01
# 机器人领养费用类型
ROBOT_ADD_COST_TYPE = 8
# 账户支出类型
PAYMENT_TYPE = 2
# 机器人被T话术
ROBOT_KICKED_WORD = '主人，您的小宠物被【{group_name}】踢出来啦，请重新拉我入群吧~'
# 机器人封号替换成功发送话术
ROBOT_BLOCKED_REPLACE_SUCCESS_WORD = '主人，【{robot_name}】受伤退休了，请您加新小宠物为好友，让他继续帮你赚钱哟。'


# @bp.route('/robot/distribution', methods=['POST'])
async def robot_distribution_view(request):
    """
    - 分配机器人
    - 更新或绑定师徒关系
    - 创建机器人用户展示表
    """
    async def exists_user_access(union_id):
        async with db.conn.acquire() as con:
            select_stmt = await con.prepare(
                '''select "robot_access".id from "robot_access" join "robot" on "robot".id="robot_access".robot_id 
                   where "robot_access".union_id=$1 and "robot".status<>3 
                   order by "robot_access".create_date desc limit 1''')
            access_id = await select_stmt.fetchval(union_id)
            return access_id

    async def update_user_access(user_access_id, sharing_user_id=None, channel=None):
        if not sharing_user_id:
            is_sharing_user = False
        else:
            is_sharing_user = True
        async with db.conn.acquire() as con:
            update_stmt = await con.prepare(
                '''update "robot_access" set sharing_user_id=case when $1 then $2 else sharing_user_id end, 
                   channel=case when $3 then $4 else channel end, 
                   update_date=now() where id=$5 returning robot_id''')
            return await update_stmt.fetchval(is_sharing_user, sharing_user_id, is_sharing_user, channel, user_access_id)

    async def create_user_access(open_id, union_id, robot_id, sharing_user_id=None, channel=None):
        async with db.conn.acquire() as con:
            insert_stmt = await con.prepare(
                '''insert into "robot_access" 
                   (id, open_id, union_id, robot_id, sharing_user_id, channel, status)
                   values (uuid_generate_v4(), $1, $2, $3, $4, $5, $6)''')
            await insert_stmt.fetch(open_id, union_id, robot_id, sharing_user_id, channel, CREATE_STATUS)

    async def robot_info(robot_id):
        '''查询机器人信息'''
        async with db.conn.acquire() as con:
            select_stmt = await con.prepare('select head_url, qr_code, wechat_no, name from "robot" where id=$1')
            robot = await select_stmt.fetchrow(robot_id)
        return robot

    open_id = request.json.get('open_id')
    union_id = request.json.get('union_id')
    if not open_id or not union_id:
        return response_json(None, code=PARAMS_ERROR_CODE, msg='缺少必要参数open_id或union_id')
    sharing_user_id = request.json.get('sharing_user_id', None)
    channel = request.json.get('channel', None)
    access_id = await exists_user_access(union_id)
    if access_id:
        if not sharing_user_id or sharing_user_id == 'null':
            sharing_user_id = None
        if not channel:
            channel = None
        robot_id = await update_user_access(access_id, sharing_user_id, channel)
    else:
        robot_id = await robot_distribution(channel=channel)
        if not robot_id:
            logger.warning(f'not match distribute robot for user [{open_id}]')
            return response_json(None, code=ROBOT_NOT_ENOUGH_CODE, msg='没有可分配的机器人')
        await create_user_access(open_id, union_id, robot_id, sharing_user_id, channel)
        await robot_today_display_record(robot_id)
    logger.info(f'distribute robot [{robot_id}] for user [{open_id}]')
    robot = await robot_info(robot_id)
    return response_json(dict(robot))


async def robot_today_display_record(robot_id):
    '''机器人今日展示次数统计, 并判断展示次数大于等于当日最大次数时，移除将该机器人置为不可分配'''
    display_key = DISPLAY_KEY_REDIS_KEY.format(today=today())
    snapshot_key = SNAPSHOT_KEY_REDIS_KEY.format(today=today())
    display_count = await redis.conn.zincrby(display_key, robot_id)
    robot_count = await redis.conn.zscore(snapshot_key, robot_id)
    if await redis.conn.ttl(display_key) == -1:
        await redis.conn.expire(display_key, KEY_TIMEOUT)
    if robot_count <= display_count:
        await remove_robot_distribute(robot_id)


async def robot_join_failed(data):
    """
    机器人今日不可入群
    1. 更新该机器人状态
    2. 查询当前机器人是否是最后一次分配机器人
        如果是：分配新机器人
        如果不是：推送最后一次分配机器人
    参数示例：
    {
        "robot_id": "20181111222222",
        "group_id": "20181111222222",
        "name": "群名称",
        "user_id": "20181111222222",
        "user_wxid": "tanxi1983",
        "avatar": "http://xxx/xxx.png",
        "reason": "已有小助手"
    }
    """
    robot_code = data.get('robot_id')
    group_code = data.get('group_id')
    user_code = data.get('user_id')
    group_name = data.get('name')
    failed_reason = data.get('reason')
    logger.info(f'robot join failed, robot_code:{robot_code}, group_code:{group_code}, user_code:{user_code}, group_name:{group_name}, reason:{failed_reason}')
    user = await get_user(user_code)
    if user is None:
        logger.error(f'robot join group failed, user not found, robot_code:{robot_code}')
        return
    user_id = user.get('id')
    user_channel = user.get('channel')
    async with db.conn.acquire() as con:
        get_robot_stmt = await con.prepare('''select id from "robot" where code = $1 and status <> 3 limit 1''')
        robot_id = await get_robot_stmt.fetchval(robot_code)
    if not robot_id:
        return response_json(None)
    await remove_robot_distribute(robot_id)
    result, new_robot_id = await check_robot_amount_distribute(user_id, user_code, user_channel, robot_code=None)
    if new_robot_id:
        robot = await get_robot(new_robot_id)
        robot_name = robot.get('name')
        qr_code = robot.get('qr_code')
        send_msg = NEW_ROBOT_WORD.format(robot_name=robot_name, group_name=group_name)
        await send_text_msg(robot_code, user_code, send_msg)
        await send_image_msg(robot_code, user_code, qr_code)
    else:
        logger.warning(f'request [robot_distribution] to distribute robot result is None')
        await send_text_msg(robot_code, user_code, NO_ROBOT_WORD)
    return response_json(None)


async def robot_add_friend(data):
    """
    1. 判断当前用户是否已经注册
    2. 已经注册，收取领养费用
    3. 未注册, 提示注册...
    参数示例：
    {
        "robot_id": "20181111222222",
        "user_id": "20181111222222",
        "nickname": "用户",
        "avatar": "http://xxx/xxx.png",
        "add_time": "1970-01-01T00:00:00"
    }
    """
    robot_code = data.get('robot_id')
    user_code = data.get('user_id')
    nickname = data.get('nickname')
    head_url = data.get('avatar')
    logger.info(f'receiver robot add friend, robot_code:{robot_code}, user_code:{user_code}')
    # added_time = request.json.get("add_time", None)
    redis_key = GPET_ROBOT_ADD_FRIEND_REDIS_KEY.format(user_code=user_code, robot_code=robot_code)
    if not await set_lock(redis_key, release_time=60):
        return
    # 判断当前用户是否已经注册过
    async with db.conn.acquire() as con:
        get_user_stmt = await con.prepare('''select id from "user" where code = $1 limit 1 ''')
        get_robot_chanel_stmt = await con.prepare('''select id, channel from "robot" where  code = $1 and status <> 3 limit 1 ''')
        user_id = await get_user_stmt.fetchval(user_code)
        robot = await get_robot_chanel_stmt.fetchrow(robot_code)
    if robot is not None:
        robot_id = robot.get('id')
        robot_channel = robot.get('channel')
        if user_id is not None:
            account_id = await get_account_id(user_id)
            # 收取领养费用
            user_income = {'amount': ROBOT_ADD_COST, 'type': ROBOT_ADD_COST_TYPE}
            await update_user_income(account_id, user_income, PAYMENT_TYPE)
            # 保存机器人加好友记录
            await save_robot_friend(user_id, robot_id)
            # 是否加封号机器人
            await add_blocked_robot(user_id, user_code, robot_code)
        else:
            user_id = await register_no_info(user_code, nickname, head_url, robot_channel)
            account_id = await get_account_id(user_id)
            user_income = {'amount': ROBOT_ADD_COST, 'type': ROBOT_ADD_COST_TYPE}
            await update_user_income(account_id, user_income, PAYMENT_TYPE)
            await generate_user_account_cache(user_code, account_id)
            # 保存机器人加好友记录
            await save_robot_friend(user_id, robot_id)
            # 保存机器人分配记录
            await save_robot_distribute(robot_id, user_id, user_code)
            # 发送信息补全链接
            content = ADD_FRIEND_WORD.format(home_url=await long_to_short(COMPLETE_LINK.format(host=settings['LOCALHOST'], user_id=user_id)))
            await send_text_msg(robot_code, user_code, content)


async def robot_kicked(data):
    '''
    1. 发送私聊话术
    2. 注销群
    {
        "robot_id": "20181111222222",
        "group_id": "20181111222222",
        "user_id": "20181111222222",
        "kick_time": "1970-01-01T00:00:00"
    }
    '''
    robot_code = data.get('robot_id')
    group_code = data.get('group_id')
    logger.info(f'robot kicked, robot_code:{robot_code}, group_code:{group_code}')
    async with db.conn.acquire() as con:
        get_group_stmt = await con.prepare('''
        select "group".id::varchar as group_id, "group".name as group_name, "user".code as user_code, "robot".code as 
        robot_code from "group" join "user" on "group".user_id = "user".id join "robot_group_map" on 
        "robot_group_map".group_id= "group".id join "robot" on "robot".id = "robot_group_map".robot_id where
         "group".code = $1 and "group".status <> 3 limit 1''')
        group = await get_group_stmt.fetchrow(group_code)
    if group is not None and robot_code == group['robot_code']:
        content = ROBOT_KICKED_WORD.format(group_name=group['group_name'])
        await send_text_msg(robot_code, group['user_code'], content)
        # 注销群
        await currency_delete_group(group['group_id'], GroupCancelReason.ROBOT_KICKED)


async def robot_blocked(data):
    """
    机器人封号
    1. 缓存机器人封号时的状态
    2. 将该机器人置为封号状态
    """
    logger.info(f'robot blocked with params:{data}')
    robot_code = data.get('robot_id')
    async with db.conn.acquire() as con:
        get_robot_user_group_stmt = await con.prepare('''
            select "group".user_id, "group".id as group_id from "robot"
            join "robot_group_map" on "robot".id = "robot_group_map".robot_id
            join "group" on robot_group_map.group_id ="group".id where "robot".code = $1 and "robot".status <> 3 and "robot_group_map".status <> 3 order by "group".user_id''')
        robot_user_group_records = await get_robot_user_group_stmt.fetch(robot_code)
        robot_user_groups = records_to_list(robot_user_group_records)
        get_robot_stmt = await con.prepare('''select id::varchar from "robot" where code = $1''')
        robot_id = await get_robot_stmt.fetchval(robot_code)
        redis_key = ROBOT_BLOCKED_REDIS_KEY.format(robot_code=robot_code)
        for user_id, items in groupby(robot_user_groups, key=itemgetter('user_id')):
            group_ids = [item('group_id') for item in items]
            await redis.conn.hset(redis_key, user_id, dumps(group_ids))
            await redis.conn.expire(redis_key, 60*60*24*7)
            for group_id in group_ids:
                await currency_delete_group(group_id, GroupCancelReason.ROBOT_BLOCKED)
        await remove_robot_distribute(robot_id)
        update_robot_stmt = await con.prepare('''update "robot" set status = 5, update_date = now() where code = $1 and status <> 3''')
        await update_robot_stmt.fetch(robot_code)


async def robot_replace_success(data):
    """
    机器人封号替换成功
    1. 更新该机器人为封号前状态
    2. 更换机器人二维码
    3. 给该机器人之前的激活的群的用户发送私聊消息(用这些用户正常的机器人)
    """
    logger.info(f'receive robot replace success with params:{data}')
    robot_code = data.get('replace_robot_id')
    qr_code = data.get('qrcode')
    redis_key = ROBOT_BLOCKED_REDIS_KEY.format(robot_code=robot_code)
    async with db.conn.acquire() as con:
        update_robot_stmt = await con.prepare('''update "robot" set qr_code = $1,  status = 1, update_date = now() where code = $2''')
        await update_robot_stmt.fetch(qr_code, robot_code)
        if not await redis.conn.exists(redis_key):
            return
        blocked_robot_name_stmt = await con.prepare('''select name from "robot" where code = $1''')
        blocked_robot_name = await blocked_robot_name_stmt.fetchval(robot_code)
        user_group_dict = await redis.conn.hgetall(redis_key)
        get_available_robot = await con.prepare('''
                select "robot".code as robot_code, "user".code as user_code from "robot_add_friend"
                join "robot" on "robot_add_friend".robot_id = "robot".id
                join "user" on "robot_add_friend".user_id = "user".id
                where "robot_add_friend".user_id = $1 and "robot_add_friend".status <> 3 and "robot".status <> 3 and "robot".status <> 5
                order by "robot_add_friend".create_date desc''')
        # get_user = await con.prepare('''select phone from "user" where id = $1 and status <> 3 limit 1''')
        for user_id, groups in user_group_dict.items():
            user_robots = await get_available_robot.fetch(user_id)
            if user_robots:
                user_robot = user_robots[0]
                available_robot_code = user_robot.get('robot_code')
                user_code = user_robot.get('user_code')
                await send_text_msg(available_robot_code, user_code, ROBOT_BLOCKED_REPLACE_SUCCESS_WORD.format(robot_name=blocked_robot_name))
                await send_image_msg(available_robot_code, user_code, qr_code)
            else:
                # 发送短信 TODO
                # phone = await get_user.fetchval(user_id)
                # if phone is not None:
                #     await send_msg(phone, )
                pass


async def get_robot(robot_id):
    async with db.conn.acquire() as con:
        robot_stmt = await con.prepare('''select name, qr_code from "robot" where id = $1 and status <> 3 limit 1''')
        return await robot_stmt.fetchrow(robot_id)


# async def latest_distribute_robot(user_id):
#     async with db.conn.acquire() as con:
#         latest_robot_id = await con.prepare('''
#         select robot_id from "robot_distribute" where user_id = $1 and status <> 3 order by create_date desc limit 1
#         ''')
#         return await latest_robot_id.fetchval(user_id)


async def get_user(user_code):
    async with db.conn.acquire() as con:
        get_user_stmt = await con.prepare('''select id, channel from "user" where code = $1 and status <> 3''')
        return await get_user_stmt.fetchrow(user_code)


async def register_no_info(friend_code, nickname, head_url, robot_channel=None):
    logger.info(f'user add friend register, code:{friend_code}')
    async with db.conn.acquire() as con:
        async with con.transaction():
            insert_user_stmt = await con.prepare('''insert into "user" (id, code, nickname, head_url, profit_flag, channel, need_remind) values (uuid_generate_v4(), $1, $2, $3, 0, $4, $5) returning id''')
            user_id = await insert_user_stmt.fetchval(friend_code, nickname, head_url, robot_channel, ujson.dumps(NEED_REMIND_JSON))
            insert_account_stmt = await con.prepare('''insert into "account" (id, user_id) values (uuid_generate_v4(), $1)''')
            await insert_account_stmt.fetch(user_id)
            return user_id


async def save_robot_friend(user_id, robot_id):
    async with db.conn.acquire() as con:
        insert_robot_friend_stmt = await con.prepare('''insert into "robot_add_friend" (id, robot_id, user_id, status) values (uuid_generate_v4(), $1, $2, 1)''')
        await insert_robot_friend_stmt.fetch(robot_id, user_id)


async def get_account_id(user_id):
    async with db.conn.acquire() as con:
        account_id_stmt = await con.prepare('''select id from "account" where user_id = $1 limit 1''')
        return await account_id_stmt.fetchval(user_id)


async def save_robot_distribute(robot_id, user_id, user_code):
    async with db.conn.acquire() as con:
        robot_distribute_stmt = await con.prepare('''insert into "robot_distribute" (id, robot_id, user_id, user_code) values (uuid_generate_v4(), $1, $2, $3)''')
        return await robot_distribute_stmt.fetch(robot_id, user_id, user_code)


async def generate_user_account_cache(user_code, account_id):
    await redis.conn.hset(USER_ACCOUNT_REDIS_KEY, user_code, account_id)


async def add_blocked_robot(user_id, user_code, robot_code):
    redis_key = ROBOT_BLOCKED_REDIS_KEY.format(robot_code=robot_code)
    if await redis.conn.hexists(redis_key, user_id):
        group_ids = ujson.loads(await redis.conn.hget(redis_key, user_id))
        async with db.conn.acquire() as con:
            get_group_names_stmt = await con.prepare('''select array_to_string(array(select name from "group" where id = any($1)), '、')''')
            group_names = get_group_names_stmt.fetch(group_ids)
            content = ADD_BLOCKED_ROBOT_WORD.format(group_names=group_names)
        await send_text_msg(robot_code, user_code, content)
        await redis.conn.delete(redis_key, user_id)


async def robot_undistributable_view(request):
    """将机器人置为不可分配，包括但不限于机器人异常"""
    robot_id = request.json.get('robot_id')
    async with db.conn.acquire() as con:
        undis_robot_stmt = await con.prepare('''update "robot" set status = 2 where id = $1''')
        await undis_robot_stmt.fetch(robot_id)
    await remove_robot_distribute(robot_id)
    return response_json(None)
