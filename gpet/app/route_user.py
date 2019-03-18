import datetime
import ujson
import asyncio
import json
import uuid

from sanic.exceptions import abort
from sanic.log import logger
from sanic_jwt.decorators import inject_user, protected

from app import db, redis
from app.send_message import send_text_msg, send_image_msg
from app.route_account import rejected_user_withdraw
from app.route_shortmsg import verify_code_check, send_msg as send_short_msg
from app.route_requests import group_mem_info
from app.common import check_robot_amount_distribute, update_user_income, get_user_by_id, get_account_info,\
    get_robot_by_id
from config import settings
from ut.response import response_json
from ut.constants import COMPLETE_CODE, RESOURCE_NOT_FOUND_CODE, PARAMS_ERROR_CODE, \
    ROBOT_NOT_ENOUGH_CODE, VERIFY_CODE_EXPIRE, VERIFY_CODE_WRONG, PHONE_HAS_REGIST, SENSITIVE_WORD_CODE, MEM_INFO_FAIL_CODE, \
    APPRENTICE_REMID_REDIS_KEY, COMPLETE_USER_REDIS_KEY, KEYWORD_KEY_REDIS_KEY, GROUP_USER_ROBOT_MAP_REDIS_KEY
from ut.utils import get_random_num, get_page_info, check_idcard, records_to_list, get_time, \
    aly_text_check, records_to_value_list, constant_data_cache


MONEY = settings['MONEY_AMOUNT']
START_DATE = settings['START_DATE']
STOP_DATE = settings['STOP_DATE']

NOT_IMPORT_MSG = '主人，小宠已经好久没有出门玩了，好无聊啊！快拉我进群吧～'
NOT_APPRENTICE_MSG = '主人，听说什么事都不用做，只靠收徒就可以躺赚百元千元佣金提成！赶快回复“收徒”，转发海报邀请好友成为你的徒弟吧~'
APPRENTICE_MSG = '收徒成功，开始坐享徒弟和徒孙的收益！赶紧召唤下一个徒弟，从此轻轻松松躺着赚钱~~回复【菜单】了解更多'
# 领取红包发送话术
RECEIVE_REDPACKET_MSG = '----👏红包领取成功！----\n\n满1元即可提现\n\n限时推广期间，拉我进入你身边的微信群，继续领红包。群越活跃红包越大，最大30元！\n作为群内智能小宠物，入群后，我会给群友提供很多有趣的功能哦。\n\n👇👇查看下图详细了解↓↓↓'
GIF_LINK = 'https://cloud.gemii.cc/lizcloud/fs/noauth/media/5c22e961a579e5001df6c5a4'
APPRENTICE = 1  # 徒弟列表
GRANDSON = 2    # 徒孙列表
# 元旦活动收益模板code
NEW_YEAR_GROUP_PROFIT_TEMPLATE_CODE = 'NEW_YEAR'
# 元旦领取红包发送话术
NEW_YEAR_REDPACKET_MSG = '----[Packet]红包领取成功！----\n\n满1元即可提现\n\n🎁🎁限时推广期间，拉我进入你身边的微信群，继续领红包。 群越热闹红包越大，最大30元！\n欢迎和群内的亲朋好友一起调戏我、刁难我，问我各种稀奇古怪的问题。\n\n👇查看下图详细了解↓↓↓'


# @bp.route('/user')
@protected()
@inject_user()
async def get_user_id(request, user):
    user_id = user.get('user_id')
    return response_json(user_id)


# @bp.route('/user/<user_id:[a-zA-Z0-9\\-]+>', methods=['PUT'])
async def modify_user(request, user_id, *args, **kwargs):
    """修改用户信息"""
    union_id = request.json.get('union_id')
    open_id = request.json.get('open_id')
    appid = request.json.get('appid')
    head_url = request.json.get('head_url')
    nick_name = request.json.get('nick_name')
    user_info = await get_user_by_id(user_id)
    logger.debug(f'modify_user:request:[{request.json}]')
    if user_info is None:
        return response_json('用户不存在', code=RESOURCE_NOT_FOUND_CODE)
    if user_info['union_id'] is not None:
        return response_json(None, msg='用户信息已补全', code=COMPLETE_CODE)
    # 根据union_id获取扫码记录
    access = await get_robot_access(union_id, status=1)
    channel = None
    sharing_user_id = None
    if access is not None:
        channel = access['channel']
        sharing_user_id = access['sharing_user_id']
        logger.debug(f'channel :{channel}, sharing_user_id:{sharing_user_id}, nick_name:{nick_name}, head_url:{head_url}')
    else:
        access_deleted = await get_robot_access(union_id, status=3)
        if access_deleted is not None:
            channel = access_deleted['channel']
            sharing_user_id = access_deleted['sharing_user_id']

    async with db.conn.acquire() as con:
        update_user = await con.prepare(
            '''update "user" 
               set union_id = $1, open_id = $2, nickname = $3, head_url = $4, channel = $5, appid = $6, 
               update_date = now() where id = $7 ''')
        await update_user.fetch(union_id, open_id, nick_name, head_url, channel, appid, user_id)
    '''保存分享关系'''
    await save_sharing_record(user_id, union_id, open_id, sharing_user_id)
    return response_json(None)


# @bp.route('/received/redpacket', methods=['GET'])
@protected()
@inject_user()
async def is_receive_redpacket(request, user):
    """是否领取过红包"""
    user_id = user.get('user_id')
    logger.debug(f'is receive redpacket user_id:{user_id}')
    async with db.conn.acquire() as con:
        get_redpacket_stmt = await con.prepare('''select id from "redpacket" where user_id = $1 limit 1''')
        redpacket = await get_redpacket_stmt.fetchval(user_id)
    if redpacket is not None:
        return response_json(True)
    return response_json(False)


# @bp.route('/receive/redpacket', methods=['GET'])
@protected()
@inject_user()
async def receive_redpacket(request, user):
    """
    领取红包
    领养协议
    """
    user_id = user.get('user_id')
    logger.debug(f'receive packet user_id:{user_id}')
    red_packet = get_random_num(0.6, 0.7, 2)
    await save_red_packet(user_id, red_packet)
    account_info = await get_account_info(user_id)
    user_income = {
        'type': 10,
        'amount': red_packet
    }
    await update_user_income(account_info['id'], user_income, remark='领取红包')
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(redpacket_notice_user(user_id), loop)
    return response_json({'red_packet': red_packet})


async def redpacket_notice_user(user_id):
    async with db.conn.acquire() as con:
        update_user_protocol = await con.prepare('''update "user" set agree_protocol = 1, update_date = now() where id = $1''')
        await update_user_protocol.fetch(user_id)
        # 发送消息通知
        user_robot_stmt = await con.prepare('''
                select "robot".code as robot_code, "user".code as user_code from "robot_add_friend" join "robot" on "robot_add_friend".robot_id = "robot".id
                join "user" on "robot_add_friend".user_id = "user".id
                where "robot_add_friend".user_id = $1 and "robot".status <> 3 order by "robot_add_friend".create_date desc limit 1''')
        user_robot = await user_robot_stmt.fetchrow(user_id)
        if user_robot is not None:
            robot_code = user_robot.get('robot_code')
            user_code = user_robot.get('user_code')
            await send_text_msg(robot_code, user_code, RECEIVE_REDPACKET_MSG)
            await asyncio.sleep(0.3)
            await send_image_msg(robot_code, user_code, GIF_LINK)


# @bp.route('/user/phone', methods=['PUT'])
@protected()
@inject_user()
async def modify_user_phone(request, user):
    """补全用户手机号"""
    user_id = user.get('user_id')
    phone = request.json.get('phone')
    code = request.json.get('code')
    logger.debug(f'complete phone :{phone},user_id:{user_id}')
    check_result = await verify_code_check(user_id, phone, code)
    if check_result == VERIFY_CODE_WRONG:
        return response_json(None, code=VERIFY_CODE_WRONG, msg='验证码错误')
    elif check_result == VERIFY_CODE_EXPIRE:
        return response_json(None, code=VERIFY_CODE_EXPIRE, msg='验证码过期')
    async with db.conn.acquire() as con:
        select_user = await con.prepare(
            '''select id from "user" where phone = $1''')
        user_result = await select_user.fetchval(phone)
        if user_result:
            return response_json(None, PHONE_HAS_REGIST, msg='手机号已注册')
        update_phone = await con.prepare(
            '''update "user" set phone= $1, update_date = now() where id = $2 ''')
        await update_phone.fetchrow(phone, user_id)
        return response_json(None, msg='success')


# @bp.route('/users/<union_id:[a-zA-Z0-9\\_-]+>/registered', methods=['GET'])
async def isregister(request, union_id):
    if not union_id:
        raise BaseException("union_id为空")
    async with request.app.db.acquire() as con:
        get_user_stmt = await con.prepare(
            '''select id from "user" where status != 3 and union_id = $1 limit 1 ''')
        record = await get_user_stmt.fetchval(union_id)
    if record is not None:
        return response_json(True)
    else:
        return response_json(False)


# @bp.route('/users/<user_id:[a-zA-Z0-9\\-]+>/block', methods=['PUT'])
async def block_user(request, user_id):
    """用户封号"""
    if not user_id:
        return response_json(None, code=PARAMS_ERROR_CODE, msg='user not found!')
    async with db.conn.acquire() as con:
        update_user_stmt = await con.prepare('''update "user" set status = 2, update_date = now() where id = $1''')
        get_account_id = await con.prepare('''select id from "account" where user_id = $1 limit 1''')
        account_id = await get_account_id.fetchval(user_id)
        await update_user_stmt.fetch(user_id)
        # 将该用户的申请提现拒绝
    await rejected_user_withdraw(account_id)
    return response_json(None)


# @bp.route('/users/block_verify')
@protected()
@inject_user()
async def is_bolcked(request, user):
    """判断用户是否封号"""
    user_id = user.get('user_id')
    if not user_id:
        return response_json(None, code=PARAMS_ERROR_CODE, msg='user not found!')
    resp = await user_is_blocked(user_id)
    return response_json(resp)


# @bp.route('/robot/show')
@protected()
@inject_user()
async def get_now_distribute_robot(request, *args, **kwargs):
    """获取用户当前绑定机器人"""
    user_id = kwargs['user']['user_id']
    users = await get_user_by_id(user_id)
    if users is None:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='用户不存在')
    result, distribute_robot_id = await check_robot_amount_distribute(user_id, users['code'], users['channel'])
    if distribute_robot_id is not None:
        robot = await get_robot_by_id(distribute_robot_id)
        params = {
            'robot_id': str(robot['id']),
            'robot_name': robot['name'],
            'qr_code': robot['qr_code'],
            'head_url': robot['head_url'],
            'wechat_no': robot['wechat_no']
        }
    else:
        return response_json(None, code=ROBOT_NOT_ENOUGH_CODE, msg='机器人不足')
    return response_json(params)


# @bp.route('/user/apprentice')
@protected()
@inject_user()
async def get_user_apprentice(request, *args, **kwargs):
    """获取徒弟徒孙列表"""
    user_id = kwargs['user']['user_id']
    leave = int(request.raw_args.get('leave'))
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    users = await get_user_by_id(user_id)
    if users is None:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='用户不存在')
    result = await user_apprentice(user_id, current_page, page_size, leave)
    if result is None:
        return response_json(data=None, msg='无数据')
    else:
        return response_json(data=result['infos'], page_info=result['page_info'])


# @bp.route('/apprentice/awakening', methods=['POST'])
@protected()
@inject_user()
async def apprentice_remind(request, *args, **kwargs):
    """徒弟唤醒"""
    user_id = request.json.get('user_id', None)
    is_import = request.json.get('is_import', None)
    is_apprentice = request.json.get('is_apprentice', None)
    redis_awakening_key = APPRENTICE_REMID_REDIS_KEY + user_id
    if await redis.conn.exists(redis_awakening_key):
        return response_json(None, msg='当日提醒一次')
    user_info = await get_user_by_id(user_id)
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            '''select "robot".code from "robot" left join "robot_add_friend" on "robot".id = "robot_add_friend".robot_id 
            where "robot_add_friend".user_id = $1 and "robot_add_friend".status !=3''')
        robot_codes = records_to_list(await select_stmt.fetch(user_id))
    if not robot_codes:
        return response_json(None, msg='机器人未找到', code=RESOURCE_NOT_FOUND_CODE)
    if (is_import is not None and not is_import) or (not is_apprentice and not is_import):
        await send_msg(robot_codes, NOT_IMPORT_MSG, user_info['code'])
    elif is_apprentice is not None and not is_apprentice:
        await send_msg(robot_codes, NOT_APPRENTICE_MSG, user_info['code'])
    await redis.conn.setex(redis_awakening_key, get_time(), 1)
    return response_json(None)


# @bp.route('/user/robots')
@protected()
@inject_user()
async def get_user_distribute_robots(request, *args, **kwargs):
    """获取当前用户已分配的机器人列表"""
    user_id = kwargs['user']['user_id']
    async with db.conn.acquire() as con:
        select_robots = await con.prepare(
            '''select "robot".id, "robot".name, "robot".wechat_no from "robot" left join "robot_distribute" on 
               "robot_distribute".robot_id = "robot".id where "robot_distribute".user_id = $1 and 
               "robot_distribute".status !=3 and "robot".status !=3''')
        robots = records_to_list(await select_robots.fetch(user_id))
        return response_json(robots)


# @bp.route('/problems')
@protected()
@inject_user()
async def get_problem_category(request, *args, **kwargs):
    """获取问题列表"""
    async with db.conn.acquire() as con:
        select_category = await con.prepare('''select id, title, seq_no, type from "user_problem_category" 
               where status !=3''')
        problem_category = records_to_list(await select_category.fetch())
        return response_json(problem_category)


# @bp.route('/user/problem', methods=['POST'])
@protected()
@inject_user()
async def save_user_problem(request, *args, **kwargs):
    """收集用户问题信息"""
    user_id = kwargs['user']['user_id']
    problem_category_id = request.json.get('problem_catgory', None)
    robot_id = request.json.get('robot_id', None)
    group_name = request.json.get('group_name', None)
    description = request.json.get('description', None)
    async with db.conn.acquire() as con:
        insert_sql = await con.prepare(
            '''insert into "user_problem" (id, user_id, problem_categoty_id, robot_id, group_name, description, status) 
               values (uuid_generate_v4(), $1, $2, $3, $4, $5, 0)''')
        await insert_sql.fetch(user_id, problem_category_id, robot_id, group_name, description)
        return response_json(None)


# @bp.route('/alt_msg')
@protected()
@inject_user()
async def get_alt_msg(request, *args, **kwargs):
    """获取@用户机器人信息"""
    user_id = kwargs['user']['user_id']
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    async with db.conn.acquire() as con:
        select_altmsg = await con.prepare(
            '''select "alt_msg".msg_id as msg_id, "group".name as group_name, "alt_msg".msg_content as msg_content, 
               "group".code as group_code, "alt_msg".status as status from "alt_msg" left join "group" on 
               "group".id="alt_msg".group_id where "group".status !=3 and "alt_msg".user_id = $1 and 
               "alt_msg".create_date >=(current_date - interval '3' day) order by "alt_msg".create_date desc
                 limit $2 offset $3''')
        msg_infos = records_to_list(await select_altmsg.fetch(user_id, page_size, current_page*page_size))
        select_count = await con.prepare(
            '''select count(1) from "alt_msg" left join "group" on "group".id="alt_msg".group_id
               where "group".status !=3 and "alt_msg".user_id = $1 and "alt_msg".create_date >=(current_date - interval '3' day)''')
        total_records = await select_count.fetchval(user_id)
        page_info = get_page_info(page_size, current_page, total_records)
        return response_json(msg_infos, page_info=page_info)


@constant_data_cache(GROUP_USER_ROBOT_MAP_REDIS_KEY, 'code')
async def map_group_relationship(code):
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select r.code as robot_code, u.code as user_code, g.id::varchar as group_id, g.code as group_code, g.user_id::varchar as user_id 
               from "group" as g join "user" u on g.user_id=u.id join "robot_group_map" map on g.id=map.group_id
               join "robot" r on r.id=map.robot_id where g.code=$1 and map.status<>3 and g.status<>3''')
        data = await st.fetchrow(code)
    if not data:
        return None
    return dict(data)


# @bp.route('/groups/<group_code:[A-Z0-9\\-]+>/msg/<msg_id:[a-zA-Z0-9\\-]+>/context')
@protected()
@inject_user()
async def get_msg_context(request, group_code, msg_id, *args, **kwargs):
    """获取消息上下文"""
    logger.info(f'msg_context,group_id:{group_code},msg_id:{msg_id}')
    group_user_robot_info = await map_group_relationship(code=group_code)
    if group_user_robot_info is None:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='群信息不存在')
    async with db.conn.acquire() as con:
        msg_st = await con.prepare('''
        with cte as (select send_date from message where id =$1) (select message.id,message.content, 
        to_char(message.send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date, message.mem_code from message,cte where 
        message.group_code =$2  and cte.send_date >= message.send_date order by message.send_date desc limit 21) union 
        (select message.id,message.content, to_char(message.send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date, 
        message.mem_code from message,cte where message.group_code = $3 and cte.send_date < message.send_date order by 
        message.send_date asc limit 20) order by send_date asc;''')
        msg = records_to_list(await msg_st.fetch(msg_id, group_code, group_code))
    user_codes = []
    for msg_detail in msg:
        if msg_detail['mem_code'] not in user_codes:
            user_codes.append(msg_detail['mem_code'])
    request_param = '|'.join(user_codes)    # 参数格式为 aaa|bbb|ccc
    mem_response = await group_mem_info(request_param)
    if int(mem_response['code']) == 100 and mem_response['content']:
        mem_info_list = mem_response['content']
    else:
        return response_json(None, MEM_INFO_FAIL_CODE, '获取群成员信息失败')
    logger.debug(f'mem_response:[{mem_info_list}]')

    mem_info_dict = {}
    for mem_info in mem_info_list:
        mem_info_dict[mem_info['id']] = {'mem_code': mem_info['id'],
                                         'head_url': mem_info['avatar'],
                                         'nickname': mem_info['nickname']}

    for msg_detail in msg:
        msg_detail.update(mem_info_dict[msg_detail['mem_code']])
        if msg_detail['mem_code'] == group_user_robot_info['robot_code'] or \
                msg_detail['mem_code'] == group_user_robot_info['user_code']:
            msg_detail['is_master'] = True
        else:
            msg_detail['is_master'] = False
        msg_detail['content'] = ujson.loads(msg_detail['content'])

    # 修改@消息为已读
    async with db.conn.acquire() as con:
        update_alt_msg = await con.prepare(
            '''update "alt_msg" set status =1 where msg_id =$1''')
        await update_alt_msg.fetchrow(msg_id)
    return response_json(data=msg)


# @bp.route('/alt_msg/reply', methods=['POST'])
@protected()
@inject_user()
async def send_alt_msg(request, *args, **kwargs):
    """回复alt消息"""
    group_code = request.json.get('group_code')
    mem_code = request.json.get('mem_code')
    content_type = int(request.json.get('type'))
    content = request.json.get('content')
    logger.info(f'send_alt_msg,group_code:{group_code},mem_code:{mem_code},content:{content}')
    if not await aly_text_check(content):
        return response_json(None, code=SENSITIVE_WORD_CODE, msg='触发敏感词')
    async with db.conn.acquire() as con:
        select_robot = await con.prepare(
            '''select "robot".code from "group"  left join "robot_group_map"  on "robot_group_map".group_id = "group".id 
               left join "robot" on "robot".id="robot_group_map".robot_id where "group".code = $1 and 
               "robot_group_map".status !=3 and "group".status !=3 and "robot".status !=3''')
        robot_code = await select_robot.fetchval(group_code)
        if robot_code is not None:
            if content_type == 3:
                await send_text_msg(robot_code, mem_code, content, group_code)
            return response_json(None, msg='回复成功')
        else:
            return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='机器人未找到')


# @bp.route('/user/groups/disciples')
@protected()
@inject_user()
async def get_user_groups_disciples(request, *args, **kwargs):
    """首页获取用户群数量和徒弟徒孙数量"""
    user_id = kwargs['user']['user_id']
    async with db.conn.acquire() as con:
        select_groups = await con.prepare(
            '''select count(1) from "group" where user_id =$1 and status !=3''')
        group_count = await select_groups.fetchval(user_id)
        select_apprentice = await con.prepare(
            '''select count(1) from "sharing_record" where
               sharing_user_id =$1 and status !=3''')
        apprentice_count = await select_apprentice.fetchval(user_id)
        select_disciple = await con.prepare(
            '''with t as (select user_id from sharing_record where sharing_user_id=$1) 
               select count(1) from sharing_record,t where sharing_record.sharing_user_id=t.user_id''')
        disciple_count = await select_disciple.fetchval(user_id)
        result = {
            'group_count': group_count,
            'disciples': int(apprentice_count) + int(disciple_count),       # 徒弟徒孙数量
            'apprentice': int(apprentice_count),                            # 徒弟数量
            'disciple': int(disciple_count)                                 # 徒孙数量
        }
        return response_json(data=result)


# @bp.route('/user/idcard', methods=['PUT'])
@protected()
@inject_user()
async def modify_user_identity(request, *args, **kwargs):
    """修改用户身份信息"""
    user_id = kwargs['user']['user_id']
    id_number = request.json.get('id_number', None)
    name = request.json.get('name', None)
    logger.debug(f'update_user_identity :user_id:{user_id},id_number:{id_number},name:{name}')
    if id_number is None or name is None or not check_idcard(id_number):
        return response_json(None, code=PARAMS_ERROR_CODE, msg='请输入正确的信息')
    val = {"id_number": id_number, "name": name}
    async with db.conn.acquire() as con:
        update_user = await con.prepare(
            '''update "user" set identity_info = $1, update_date = now() where id= $2''')
        await update_user.fetch(ujson.dumps(val), user_id)
    return response_json(None, msg='修改成功')


# @bp.route('/user/refresh/<union_id:[a-zA-Z0-9\\_-]+>', methods=['PUT'])
@protected()
@inject_user()
async def refresh_user(request, union_id, *args, **kwargs):
    """刷新用户信息"""
    appid = request.json.get('appid')
    head_url = request.json.get('head_url')
    nick_name = request.json.get('nick_name')
    open_id = request.json.get('open_id')
    async with db.conn.acquire() as con:
        select_user = await con.prepare(
            '''select id::varchar from "user" where union_id = $1 and status!=3''')
        user_id = await select_user.fetchval(union_id)
        if user_id is None:
            return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='用户不存在')
        update_user = await con.prepare(
            '''update "user" set appid =$1, head_url =$2, nickname =$3, open_id =$4, update_date = now()
               where union_id =$5''')
        await update_user.fetch(appid, head_url, nick_name, open_id, union_id)
    return response_json(None)


# @bp.route('/alt/switch', methods=['PUT'])
@protected()
@inject_user()
async def alt_switch(request, *args, **kwargs):
    """设置用户@消息开关"""
    user_id = kwargs['user']['user_id']
    switch = int(request.json.get('alt_switch'))
    if switch is None:
        return response_json(None, code=PARAMS_ERROR_CODE, msg='参数错误')
    async with db.conn.acquire() as con:
        update_user = await con.prepare(
            '''update "user" set alt_switch = $1, update_date = now() where id = $2''')
        await update_user.fetchrow(switch, user_id)
    return response_json(switch)


# @bp.route('/alt/switch')
@protected()
@inject_user()
async def alt_switch_info(request, *args, **kwargs):
    user_id = kwargs['user']['user_id']
    user_info = await get_user_by_id(user_id)
    if user_info is not None:
        switch = user_info['alt_switch']
        return response_json(switch)


async def send_msg(robot_codes, msg, mem_code):

    logger.debug(f'apprentice_remind, {msg}')
    """发送消息"""
    if isinstance(robot_codes, list):
        for robot_code in robot_codes:
            await send_text_msg(robot_code['code'], mem_code, msg)


async def user_apprentice(user_id, current_page, page_size, leave):
    """获取用户徒弟徒孙信息"""
    if user_id is None:
        return None
    async with db.conn.acquire() as con:
        share_records = []
        count = 0
        if leave == APPRENTICE:
            select_stmt = await con.prepare(
                '''select "sharing_record".user_id::varchar , to_char("sharing_record".create_date, 'YYYY-MM-DD HH24:MI:SS') 
                   as create_date, "user".nickname, "user".need_remind from "sharing_record" left join "user" on 
                   "user".id = "sharing_record".user_id where "sharing_record".status != 3 and 
                   "sharing_record".sharing_user_id = $1 order by "sharing_record".create_date desc limit $2 offset $3''')
            share_records = records_to_list(await select_stmt.fetch(user_id, page_size, current_page*page_size))
            select_count = await con.prepare(
                '''select count(1) from "sharing_record" 
                   where status != 3 and sharing_user_id = $1''')
            count = await select_count.fetchval(user_id)
        elif leave == GRANDSON:
            select_stmt = await con.prepare(
                '''with t as (select user_id from "sharing_record" where status != 3 and sharing_user_id = $1 )
                   select "sharing_record".user_id::varchar , to_char("sharing_record".create_date, 'YYYY-MM-DD HH24:MI:SS')
                   as create_date, "user".nickname, "user".need_remind from t,"sharing_record" left join "user" on "user".id = "sharing_record".user_id
                   where "sharing_record".status != 3 and "sharing_record".sharing_user_id = t.user_id 
                   order by "sharing_record".create_date desc limit $2 offset $3''')
            share_records = records_to_list(await select_stmt.fetch(user_id, page_size, current_page*page_size))
            select_count = await con.prepare(
                '''select count(1) from "sharing_record" 
                   where status != 3 and sharing_user_id in (select user_id from "sharing_record" where status != 3 and 
                   sharing_user_id = $1)''')
            count = await select_count.fetchval(user_id)
        result = {
            'infos': await disciple_result_params(share_records),
            'page_info': get_page_info(page_size, current_page, count)
        }
    return result


async def disciple_result_params(share_records):
    """整合返回参数"""
    infos = []
    if isinstance(share_records, list):
        if not share_records:
            return None
        for record in share_records:
            need_remind = ujson.loads(record['need_remind'])
            info = {
                "create_date": record['create_date'],
                "is_import": True if need_remind.get('is_import') == 1 else False,
                "is_apprentice": True if need_remind.get('is_apprentice') == 1 else False,
                "name": record['nickname'],
                "user_id": record['user_id'],
                "is_remind": 0 if (await redis.conn.exists(APPRENTICE_REMID_REDIS_KEY + record['user_id']) or
                                   (need_remind.get('is_import') == 1 and need_remind.get('is_apprentice') == 1)) else 1
            }
            infos.append(info)
        return infos


async def save_sharing_record(user_id, union_id, open_id, sharing_user_id):
    """保存分享关系"""
    async with db.conn.acquire() as con:
        insert_sql = await con.prepare(
            '''insert into "sharing_record" (id, user_id, union_id, open_id, sharing_user_id, status)
               values (uuid_generate_v4(), $1, $2, $3, $4, $5)''')
        await insert_sql.fetch(user_id, union_id, open_id, sharing_user_id, 1)

    if sharing_user_id is None:
        return None
    user_info = await get_user_by_id(sharing_user_id)
    logger.debug(f'sharing_user_id:{sharing_user_id}')
    async with db.conn.acquire() as con:
        select_count = await con.prepare(
            '''select count(1) from "sharing_record" where sharing_user_id = $1 and status !=3''')
        count = await select_count.fetchval(sharing_user_id)
        if count >= 1:
            update_user = await con.prepare(
                '''update "user" set need_remind = jsonb_set(need_remind, $1, $2::jsonb), update_date = now() 
                   where id = $3''')
            await update_user.fetchrow({"is_apprentice"}, '1', sharing_user_id)
        select_robot = await con.prepare(
            '''with c as (select robot_id from "robot_add_friend"
               where user_id = $1 and status !=3 order by create_date desc limit 1)
               select robot.code from c,robot where robot.id = c.robot_id and robot.status != 3''')
        robot_code = await select_robot.fetchval(sharing_user_id)
        await send_text_msg(robot_code, user_info['code'], APPRENTICE_MSG)
        select_grand_father = await con.prepare('''select "user".code from "sharing_record" left join "user" on 
        "user".id= "sharing_record".sharing_user_id where "sharing_record".user_id = $1''')
        grand_father_id = await select_grand_father.fetchval(sharing_user_id)
        redis_value = {
            'father_id': user_info['code'],
            'grand_father_id': grand_father_id
        }
        await redis.conn.hset(COMPLETE_USER_REDIS_KEY, user_id, ujson.dumps(redis_value))  # 用户的师傅、师爷关系缓存


async def save_red_packet(user_id, red_packet):
    """发红包"""
    if user_id is None or red_packet is None:
        return None
    async with db.conn.acquire() as con:
        insert_sql = await con.prepare(
            '''insert into "redpacket" (id, user_id, amount, status) 
               values (uuid_generate_v4(), $1, $2, $3)''')
        await insert_sql.fetchrow(user_id, red_packet, 1)


async def get_robot_access(union_id, status=1):
    """根据uniond_id获取扫码记录信息"""
    if union_id is None:
        return None
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            '''select * from "robot_access" 
               where status = $2 and union_id = $1''')
        return await select_stmt.fetchrow(union_id, status)


async def user_is_blocked(user_id):
    """返回值 True代表封号， False代表正常"""
    async with db.conn.acquire() as con:
        get_user_stmt = await con.prepare(
            '''select status from  "user" where id = $1 limit 1''')
        status = await get_user_stmt.fetchval(user_id)
    if status == 2:
        return True
    else:
        return False


async def member_info_call_back(data):
    """群成员信息回调"""
    group_members = data
    if isinstance(group_members, list):
        mem_count = len(group_members)
        async with db.conn.acquire() as con:
            update_mem_count = await con.prepare('''update "group" set mem_count = $1 where code = $2 and status <> 3''')
            await update_mem_count.fetchrow(mem_count, group_members[0]["group_id"])
        for member in group_members:
            if member['is_admin']:
                async with db.conn.acquire() as con:
                    update_group = await con.prepare('''update "group" set owner_user_code = $1 where code = $2 and status <>3''')
                    await update_group.fetchrow(member['user_id'], member['group_id'])


def is_empty(key_list, my_dict):
    """
    判断key_list中的元素是否存在为空的情况
    """
    for key in key_list:
        if key not in my_dict or not my_dict[key]:
            return True
    return False


async def find_user_key_words(user_id):
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select keyword from "user" where id=$1''')
        user_keywords = await select_stmt.fetchrow(user_id)

    user_keywords = user_keywords['keyword']
    if user_keywords is not None:
        user_keywords = json.loads(user_keywords)
    return user_keywords


async def check_keyword(keyword):
    result = True
    for item in keyword:
        result = await aly_text_check(item)
        if not result:
            break
    return result


async def group_keyword(user_id):
    """群对应的关键字"""
    user_keywords = await find_user_key_words(user_id)
    group_keyword_dict = {}
    if user_keywords is not None:
        for key, value in user_keywords.items():
            reply_content = value['reply_content']
            for group_id in value['group_codes']:
                for item in value['keywords']:
                    if group_id not in group_keyword_dict:
                        group_keyword_dict[group_id] = [{"keyword": item, "uuid": key, "reply_content": reply_content}]
                    else:
                        group_keyword_dict[group_id].append({"keyword": item, "uuid": key, "reply_content": reply_content})

    return group_keyword_dict


# @bp.route('/keywords', methods=['GET'])
@protected()
@inject_user()
async def keyword_list(request, user):
    """查询关键字列表"""
    user_id = user.get('user_id')
    user_keywords = await find_user_key_words(user_id)
    keywords_list = []
    if user_keywords is not None:
        for key, value in user_keywords.items():
            result_dict = {
                'batch_id': key,
                'keywords': value['keywords'],
                'bind_group_counts': len(value['group_codes']),
                'reply_content': value['reply_content'],
                'trigger_times': value['trigger_times'],
                'group_codes': value['group_codes']
            }

            keywords_list.append(result_dict)

    return response_json(keywords_list)


# @bp.route('/keywords/<id:[a-z-A-Z-0-9\\-]+>', methods=['GET'])
@protected()
@inject_user()
async def keyword_detail(request, user, id):
    """查询关键字详情"""
    user_id = user.get('user_id')
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select keyword->$1 as keyword from "user" where id= $2 ''')
        result = dict(await select_stmt.fetchrow(id, user_id))
    keyword = result['keyword']
    if keyword is not None:
        keyword = json.loads(keyword)
        keyword['id'] = id
    return response_json(keyword)


# @bp.route('/keywords', methods=['POST'])
@protected()
@inject_user()
async def create_keyword(request, user):
    """增加关键字列表"""
    if is_empty(['keywords', 'reply_content', 'group_codes'], request.json):
        return response_json({}, PARAMS_ERROR_CODE, msg='请求参数错误')
    user_id = user.get('user_id')
    keywords = request.json.get('keywords')
    reply_content = request.json.get('reply_content')
    group_codes = request.json.get('group_codes')
    # 关键字校验
    check_keyword_list = keywords[:]
    check_keyword_list.append(reply_content)
    if not await check_keyword(check_keyword_list):
        return response_json(None, SENSITIVE_WORD_CODE, msg='设置内容涉及敏感词')
    # 保证群和关键字作为唯一约束
    user_keywords = await find_user_key_words(user_id)
    batch_id = str(uuid.uuid4())
    st = {batch_id: {"keywords": keywords,
                     "reply_content": reply_content,
                     "group_codes": group_codes,
                     "trigger_times": 0}}

    st = json.dumps(st)
    if user_keywords is not None:
        for key, value in user_keywords.items():
            set_group = set(group_codes) & set(value['group_codes'])
            set_key = set(keywords) & set(value['keywords'])
            if len(list(set_key)) > 0 and len(list(set_group)) > 0:
                return response_json({}, PARAMS_ERROR_CODE, msg='群的关键字不能重复')

    async with db.conn.acquire() as con:
        if user_keywords is not None:
            update_stmt = await con.prepare('''
        update "user" set keyword = keyword || $1, update_date=now() where id=$2''')
        else:
            update_stmt = await con.prepare('''
    update "user" set keyword = $1, update_date=now() where id=$2''')
        await update_stmt.fetch(st, user_id)

    group_keyword_dict = await group_keyword(user_id)
    for key, value in group_keyword_dict.items():
        val = json.dumps(value)
        await redis.conn.hset(KEYWORD_KEY_REDIS_KEY, key, val)
    return response_json('SUCCESS')


# @bp.route('/keywords', methods=['PUT'])
@protected()
@inject_user()
async def modify_keyword(request, user):
    """修改关键字"""
    user_id = user.get('user_id')
    if is_empty(['id', 'keywords', 'reply_content', 'group_codes'], request.json):
        return response_json({}, PARAMS_ERROR_CODE, msg='请求参数错误')
    batch_id = request.json.get('id')
    keywords = request.json.get('keywords')
    reply_content = request.json.get('reply_content')
    group_codes = request.json.get('group_codes')
    logger.debug(f'update user [{user_id}] keywords [{batch_id}] to  [{keywords}] to group [{group_codes}] keywords reply_content is [{reply_content}]')
    before_update_group = []
    # 敏感词校验
    check_keyword_list = keywords[:]
    check_keyword_list.append(reply_content)
    if not await check_keyword(check_keyword_list):
        return response_json(None, SENSITIVE_WORD_CODE, msg='设置内容涉及敏感词')
    # 保证群和关键字作为唯一约束
    user_keywords = await find_user_key_words(user_id)
    if user_keywords is None:
        return response_json({}, PARAMS_ERROR_CODE, msg='请求参数错误')
    value_dict = {"keywords": keywords, "reply_content": reply_content, "group_codes": group_codes, "trigger_times": 0}

    for key, value in user_keywords.items():
        if key == batch_id:
            before_update_group = value['group_codes']
            continue
        set_group = set(group_codes) & set(value['group_codes'])
        set_key = set(keywords) & set(value['keywords'])
        if len(list(set_key)) > 0 and len(list(set_group)) > 0:
            return response_json({}, PARAMS_ERROR_CODE, msg='群的关键字不能重复')

    async with db.conn.acquire() as con:
        insert_stmt = await con.prepare('''
       UPDATE "user" SET keyword = jsonb_set(keyword, $1, $2::jsonb), update_date = now() where id=$3''')
        await insert_stmt.fetchrow({batch_id}, json.dumps(value_dict), user_id)

    group_keyword_dict = await group_keyword(user_id)
    set3 = set(before_update_group) - set(group_keyword_dict.keys())
    for item in list(set3):
        await redis.conn.hdel(KEYWORD_KEY_REDIS_KEY, item)

    for key, value in group_keyword_dict.items():
        val = json.dumps(value)
        await redis.conn.hset(KEYWORD_KEY_REDIS_KEY, key, val)

    return response_json('SUCCESS')


# @bp.route('/keywords', methods=['DELETE'])
@protected()
@inject_user()
async def delete_keyword(request, user):
    """删除关键字"""
    user_id = user.get('user_id')
    if is_empty(['id'], request.json):
        return response_json({}, PARAMS_ERROR_CODE, msg='请求参数错误')
    batch_id = request.json.get('id')
    logger.debug(f'delete user [{user_id}] keywords uuid is [{batch_id}]')

    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select keyword->$1 as keyword from "user" where id= $2 ''')
        keywords_detail = dict(await select_stmt.fetchrow(batch_id, user_id))

    async with db.conn.acquire() as con:
        update_stmt = await con.prepare('''
        UPDATE "user" SET keyword = keyword - $1, update_date = now() where id=$2 ''')
        await update_stmt.fetch(batch_id, user_id)

    group_keyword_dict = await group_keyword(user_id)
    group_codes = json.loads(keywords_detail['keyword'])
    for item in group_codes['group_codes']:
        await redis.conn.hdel(KEYWORD_KEY_REDIS_KEY, item)

    if len(group_keyword_dict) != 0:
        for key, value in group_keyword_dict.items():
            val = json.dumps(value)
            await redis.conn.hset(KEYWORD_KEY_REDIS_KEY, key, val)
    return response_json('SUCCESS')
