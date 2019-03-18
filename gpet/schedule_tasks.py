import asyncio
import datetime
import logging.config
import time
import ujson
from itertools import groupby
from operator import itemgetter

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.common import batch_update_active_user_operate, today
from config import settings, job_settings
from ut.constants import MSGTYPE, TASK_MSG_MONITOR_REDIS_KEY, STATISTICS_USER_GROUPS_REDIS_KEY, SUB_EXPIRE_REDIS_KEY, \
    TIMING_NOTICE_STAR_REDIS_KEY, USER_OPT_DAY_REDIS_KEY, UserOpt, NO_CLICK_GROUPS_REDIS_KEY
from ut.log_config import LOGGING_CONFIG_FILE_HANDLER
from ut.base import db, redis
from app.wechat_pay import weixin_transfers
from app.send_message import send_text_msg, send_image_msg, send_url_link_msg, send_mini_program_msg
from app.settlement import users_groups_settlement
from ut.utils import records_to_list, yesterday, records_to_value_list
from app.route_requests import get_robot_quota, get_robot_info
from app.route_group import inner_delete_groups


if settings['DEBUG']:
    level = logging.DEBUG
else:
    level = logging.INFO


logging.config.dictConfig(LOGGING_CONFIG_FILE_HANDLER)
logger = logging.getLogger('tasks')
logger.setLevel(level)

scheduler = AsyncIOScheduler()

MSG_SEND_SUCCESS = '100'

SEND_FAILED = 2           # 信息发送失败
SEND_SUCCESS = 1          # 信息发送成功

PAYMENT_DESC = '微小宠奖励金提现'
WITHDRAWING = 0           # 提现中
WITHDRAW_SUCCESSED = 1    # 提现成功
WITHDRAW_FAILED = 2       # 提现失败
REVIEW_SUCCESSED = 1      # 审核成功
PAYMENT_TYPE = 2          # 支出类型
WITHDRAW_AMOUNT_TYPE = 9  # 提现费用类型

MASS_MSG_TIMEOUT = '由于您长时间未发送图片/链接/小程序，已退出群发消息。如需再次使用，可回复【6】'
CUSTOMER_MSG_TIMEOUT = '由于您长时间无应答，系统已结束您的对话，欢迎您下次咨询~'
NOT_IMPORT_GROUP_MSG = '还在等什么？现在拉我进群，然后在群内发送任意消息完成激活，我来帮你赚钱！'
IMPORT_GROUP_NOT_APPRENTICE = '听说什么事都不用做，只靠收徒就可以躺赚百元千元佣金提成！赶快转发海报邀请好友成为你的徒弟吧~'
POST_URL = ''.join([settings['LOCALHOST'] + '/user/{user_id}/poster'])

NOT_IMPORT_GROUP = 0    # 未导群
HAS_IMPORT_GROUP = 1    # 已导群
NOT_APPRENTICE = 0      # 未收徒
HAS_APPRENTICE = 1      # 已收徒


async def init_connect(_loop):
    await db.init_app(_loop, settings['DATABASES'])
    redis.init_app(_loop, settings['REDIS'])


async def cancel_connect(_loop):
    await db.conn.close()
    redis.conn.connection_pool.disconnect()
    scheduler.shutdown()


async def wait_for_message(pubsub):
    while True:
        msg = await pubsub.get_message()
        if msg is not None:
            if msg['channel'] == SUB_EXPIRE_REDIS_KEY and str(msg['data']).startswith('GPET:MASS_MESSAGE_'):
                mem_code, robot_code = msg['data'].split('_')[-2:]
                await send_text_msg(robot_code, mem_code, MASS_MSG_TIMEOUT)
            elif msg['channel'] == SUB_EXPIRE_REDIS_KEY and str(msg['data']).startswith('GPET:CUSTOMER_MESSAGE_'):
                mem_code, robot_code = msg['data'].split('_')[-2:]
                await send_text_msg(robot_code, mem_code, CUSTOMER_MSG_TIMEOUT)
        await asyncio.sleep(0.001)


async def monitor_redis_key_expire():
    '''监听key过期消息事件'''
    logger.info('start moniotr redis key expire...')
    r = redis.conn.pubsub()
    await r.psubscribe('__keyevent@0__:expired')
    await wait_for_message(r)


async def monitor_task_message():
    '''监听群发消息发送任务'''
    timestamp = int(time.time())
    start = timestamp - 30
    end = timestamp + 30
    data = []
    task_ids = await redis.conn.zrangebyscore(TASK_MSG_MONITOR_REDIS_KEY, start, end)
    if task_ids:
        logger.info(f'prepare send tasks count: {len(task_ids)}')
    for task_id in task_ids:
        data.append(deal_task_message(task_id))
    if data:
        results = await asyncio.gather(*data)
        logger.info(f'tasks {task_ids} results: {results}')


async def deal_task_message(task_id):
    '''处理单个task消息'''
    async def update_task_status(task_id, status):
        async with db.conn.acquire() as con:
            task_stmt = await con.prepare('update "group_task" set status=$1 where id=$2')
            await task_stmt.fetchrow(status, task_id)

    async def get_task(task_id):
        async with db.conn.acquire() as con:
            task_stmt = await con.prepare('select group_ids, content from "group_task" where id=$1 and status<>3')
            task = await task_stmt.fetchrow(task_id)
        return task

    async def prepare_send_msg_data(group_code):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select r.code as robot_code, g.code as group_code from "group" as g 
                   join "robot_group_map" map on g.id=map.group_id
                   join "robot" r on r.id=map.robot_id where g.code=$1 and map.status<>3 and g.status<>3''')
            data = await st.fetchrow(group_code)
        return data

    await redis.conn.zrem(TASK_MSG_MONITOR_REDIS_KEY, task_id)
    task = await get_task(task_id)
    if not task:
        logger.warning(f'task [{task_id}] not match, maybe task has been canceled')
        return False
    contents = ujson.loads(task['content'])
    group_codes = ujson.loads(task['group_ids'])
    logger.debug(f'task [{task_id}] prepare send group count: [{len(group_codes)}]')
    for group_code in group_codes:
        data = await prepare_send_msg_data(group_code)
        if not data:
            logger.warning(f'not match task [{task_id}] map group [{group_code}], maybe group has been deleted')
            continue
        robot_code = data['robot_code']
        group_code = data['group_code']
        logger.debug(f'prepare task [{task_id}] send msg to group [{group_code}] use robot [{robot_code}]')
        for c in contents:
            if c['type'] == MSGTYPE.TEXT:
                resp = await send_text_msg(robot_code, member_code=[], content=c['content'], group_code=group_code)
            elif c['type'] == MSGTYPE.IMAGE:
                resp = await send_image_msg(robot_code, member_code=[], content=c['content'], group_code=group_code)
            elif c['type'] == MSGTYPE.LINK:
                resp = await send_url_link_msg(robot_code, member_code=[], content=c['content'],
                                               title=c['title'], href=c['url'], desc=c['desc'], group_code=group_code)
            elif c['type'] == MSGTYPE.MINI_PROGRAM:
                resp = await send_mini_program_msg(robot_code, member_code=[], content=c['content'], title=c['title'],
                                                   href=c['url'], desc=c['desc'], group_code=group_code)
            else:
                resp = {'code': '500'}             # 未找到对应的类型时，返回错误码
            if resp['code'] != MSG_SEND_SUCCESS:
                logger.warning(f'task [{task_id}] send msg [{c["type"]}] to gorup [{group_code}] get error resp {resp}')
    await update_task_status(task_id, SEND_SUCCESS)
    return True


async def deal_user_withdraw_task():
    '''定时处理提现中的记录，打款到用户'''
    async def withdraw_statistics(user_id):
        '''单个用户提现统计'''
        async with db.conn.acquire() as con:
            wd_stmt = await con.prepare(
                '''select id, account_id, amount from "account_withdraw"
                   where user_id = $1 and status = $2 and review_status = $3 
                   order by account_id, create_date''')
            wd_datas = await wd_stmt.fetch(user_id, WITHDRAWING, REVIEW_SUCCESSED)
        return wd_datas

    async def withdraw_successed_account(account_id, withdraw_id, amount, msg):
        '''打款提现成功'''
        settle_date = datetime.datetime.now().date()
        async with db.conn.acquire() as con:
            async with con.transaction():
                wd_ut = await con.prepare(
                    '''update "account_withdraw" set status = $1, withdraw_resp=$2, update_date=now(), paid_date=now()
                       where id = $3''')
                await wd_ut.fetchrow(WITHDRAW_SUCCESSED, msg, withdraw_id)
                acc_st = await con.prepare('select balance_amount from "account" where id=$1 for update')
                acc_data = await acc_st.fetchval(account_id)
                slip_it = await con.prepare(
                    '''insert into "account_slip" 
                      (id, account_id, balance_type, change_amount, balance, amount_type, remark, settle_date, status) 
                      values (uuid_generate_v4(), $1, $2, $3, $4, $5, $6, $7, 1)''')
                await slip_it.fetchrow(account_id, PAYMENT_TYPE, amount, acc_data, WITHDRAW_AMOUNT_TYPE, PAYMENT_DESC, settle_date)
                acc_ut = await con.prepare(
                    '''update "account" set withdrawing_amount=withdrawing_amount - $1::numeric, 
                       update_date=now() where id=$2''')
                await acc_ut.fetchrow(amount, account_id)

    async def withdraw_failed_account(account_id, withdraw_id, amount, msg):
        '''打款提现失败'''
        async with db.conn.acquire() as con:
            async with con.transaction():
                wd_ut = await con.prepare(
                    '''update "account_withdraw" set status = $1, withdraw_resp=$2, update_date=now(), paid_date=now() 
                       where id = $3''')
                await wd_ut.fetchrow(WITHDRAW_FAILED, msg, withdraw_id)
                acc_ut = await con.prepare(
                    '''update "account" set withdrawing_amount=withdrawing_amount - $1::numeric, 
                       balance_amount = balance_amount + $2::numeric, update_date=now() where id=$3''')
                await acc_ut.fetchrow(amount, amount, account_id)

    async def statistics_withdraw_user():
        '''统计打款用户'''
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select distinct "account_withdraw".user_id from "account_withdraw" 
                   join "user" on "user".id="account_withdraw".user_id
                   where "account_withdraw".status = $1 and "account_withdraw".review_status = $2 
                   and "user".status=1 group by "account_withdraw".user_id''')
            wd_users = await st.fetch(WITHDRAWING, REVIEW_SUCCESSED)
        logger.info(f'statistics user withdraw count: {len(wd_users)}')
        return records_to_list(wd_users)

    async def get_user_info(user_id):
        '''获取用户信息'''
        async with db.conn.acquire() as con:
            st = await con.prepare('select id, open_id, appid from "user" where id=$1')
            user = await st.fetchrow(user_id)
        return user

    async def payment_for_user(user_id):
        '''用户打款入口'''
        user = await get_user_info(user_id)
        for wd in await withdraw_statistics(user_id):
            trade_no = int(time.time() * 1000)
            try:
                pay_res, detail = await weixin_transfers(float(wd['amount']), trade_no, PAYMENT_DESC, user['open_id'], user['appid'])
                logger.info(f'''user [{user_id}] withdraw: [{wd["id"]}] amount: [{wd["amount"]}] 
                                weixin response: {pay_res}, detail: {detail}''')
                msg = ujson.dumps(detail)
                if not pay_res:
                    await withdraw_failed_account(wd['account_id'], wd['id'], wd['amount'], msg)
                else:
                    await withdraw_successed_account(wd['account_id'], wd['id'], wd['amount'], msg)
            except Exception as e:
                logger.error(f'user [{user_id}] withdraw: [{wd["id"]}] occur error: {e}')

    withdraw_users = await statistics_withdraw_user()
    user_counts = len(withdraw_users)
    for i in range(0, user_counts, 50):
        tasks = []
        each_withdraw_users = withdraw_users[i:i+50]
        for user in each_withdraw_users:
            tasks.append(payment_for_user(user['user_id']))
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)

    # tasks = []
    # for user in await statistics_withdraw_user():
    #     tasks.append(payment_for_user(user['user_id']))
    # await asyncio.gather(*tasks)


async def yesterday_group_chat_volume_task():
    '''处理昨日用户所属群中的成员会话量'''
    async def chat_statistics():
        async with db.conn.acquire() as con:
            chat_stmt = await con.prepare(
                '''select g.user_id, tmp.group_code as code, tmp.mem_count as counts  
                   from (select m.group_code, count(distinct mem_code) as mem_count from "message" m
                   where m.send_date >= timestamp 'yesterday' and m.send_date < timestamp 'today'
                   group by m.group_code) tmp join "group" g on g.code=tmp.group_code 
                   where g.status<>3 order by g.user_id''')
            chats = await chat_stmt.fetch()
        return records_to_list(chats)

    async def deal_each_user_chat_volumn(key, user_id, group_datas):
        datas = await redis.conn.hget(key, user_id)
        results = {}
        if not datas:
            for group in group_datas:
                results.update({group['code']: {'msg_counts': group['counts']}})
        else:
            datas = ujson.loads(datas)
            for group in group_datas:
                exist_group = datas.get(group['code'])
                if not exist_group:
                    results.update({group['code']: {'msg_counts': group['counts']}})
                else:
                    exist_group.update({'msg_counts': group['counts']})
                    results.update({group['code']: exist_group})
        logger.debug(f'user msg statistic: {results}')
        await redis.conn.hset(static_key, user_id, ujson.dumps(results))

    static_key = STATISTICS_USER_GROUPS_REDIS_KEY.format(today=yesterday())
    for user_id, group_datas in groupby(await chat_statistics(), key=itemgetter('user_id')):
        await deal_each_user_chat_volumn(static_key, user_id, group_datas)


async def user_remind():
    '''用户提醒,定时扫描'''
    logger.info(f'user_remind start!')
    async with db.conn.acquire() as con:
        select_user = await con.prepare('''
        select id, code, need_remind, create_date from "user" where need_remind @> '{"remind":1}'::jsonb and 
        (need_remind @> '{"is_import":0}'::jsonb or (need_remind @> '{"is_import":1}'::jsonb and 
        need_remind @> '{"is_apprentice":0}'::jsonb)) and extract(epoch FROM (now() - create_date)) > 3600*24 and 
        extract(epoch FROM (now() - create_date)) < 3600*36''')
        users = records_to_list(await select_user.fetch())
    if not users:
        logger.debug(f'user_remind users not exist!')
        return
    logger.info(f'need remind users counts: {len(users)}')
    import_remind_user = []
    apprentice_remind_user = []
    for user in users:
        async with db.conn.acquire() as con:
            select_add_robot = await con.prepare(
                '''select "robot".code from "robot_add_friend" left join "robot" on "robot".id = robot_add_friend.robot_id 
                   where "robot_add_friend".user_id = $1 order by robot_add_friend.create_date desc limit 1''')
            robot_code = await select_add_robot.fetchval(user['id'])
        need_remind = ujson.loads(user['need_remind'])
        if need_remind['is_import'] == NOT_IMPORT_GROUP:
            await send_text_msg(robot_code, user['code'], NOT_IMPORT_GROUP_MSG)
            import_remind_user.append(user['id'])
        elif need_remind['is_import'] == HAS_IMPORT_GROUP and need_remind['is_apprentice'] == NOT_APPRENTICE:
            url = POST_URL.format(user_id=user['id'])
            await send_image_msg(robot_code, user['code'], url)
            await send_text_msg(robot_code, user['code'], IMPORT_GROUP_NOT_APPRENTICE)
            apprentice_remind_user.append(user['id'])
    if import_remind_user:
        async with db.conn.acquire() as con:
            update_user = await con.prepare(
                '''update "user" set need_remind = jsonb_set(need_remind, $1, $2::jsonb), update_date = now()
                   where id = any($3)''')
            await update_user.fetchrow({"remind"}, '0', import_remind_user)
    if apprentice_remind_user:
        async with db.conn.acquire() as con:
            update_user = await con.prepare(
                '''update "user" set need_remind = jsonb_set(need_remind, $1, $2::jsonb), update_date = now()
                   where id = any($3)''')
            await update_user.fetchrow({"remind"}, '0', apprentice_remind_user)


async def notice_group_star_yesterday_night():
    logger.info(f'notice yesterday night group star start!')
    if await redis.conn.exists(TIMING_NOTICE_STAR_REDIS_KEY):
        length = await redis.conn.llen(TIMING_NOTICE_STAR_REDIS_KEY)
        logger.info(f'notice yesterday night group star, len:{length}')
        while True:
            notice = await redis.conn.lpop(TIMING_NOTICE_STAR_REDIS_KEY)
            if not notice:
                break
            notice = ujson.loads(notice)
            robot_code = notice.get('robot_code')
            user_code = notice.get('user_code')
            msg_content = notice.get('msg_content')
            msg_content_url = notice.get('msg_content_url')
            msg_content_new_year = notice.get('msg_content_new_year')
            await send_text_msg(robot_code, user_code, msg_content)
            if msg_content_url is not None:
                await send_image_msg(robot_code, user_code, msg_content_url)
            if msg_content_new_year is not None:
                await send_text_msg(robot_code, user_code, msg_content_new_year)


async def sync_robot_info():
    logger.info(f'sync robot info start!')
    async with db.conn.acquire() as con:
        get_robot_stmt = await con.prepare('''select code from "robot" where status <> 3''')
        robots = await get_robot_stmt.fetch()
        robot_codes = records_to_value_list(robots, 'code')
        logger.info(f'sync robot count:{len(robot_codes)}')
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(sync_robot(robot_codes), loop)
    logger.info(f'sync robot end!')


async def sync_robot(robot_codes):
    for index in range(0, len(robot_codes), 2000):
        tasks = []
        items = robot_codes[index: index+2000]
        for robot_code in items:
            tasks.append(task_sync_robot(robot_code))
        await asyncio.gather(*tasks)


async def task_sync_robot(robot_code):
    try:
        # 同步机器人额度信息
        robot_quota_resp = await get_robot_quota(robot_code)
        if int(robot_quota_resp.get('code')) != 100:
            return
        else:
            robot_count = len(robot_quota_resp.get('content'))
        # 同步机器人基本信息
        robot_info_resp = await get_robot_info(robot_code)
        if int(robot_info_resp.get('code')) != 100:
            return
        else:
            robot_info = robot_info_resp.get('content')
            nick_name = robot_info.get('nickname')
            wechat_no = robot_info.get('wxid')
            head_url = robot_info.get('avatar')
            qr_code = robot_info.get('qrcode')
        async with db.conn.acquire() as con:
            update_robot_stmt = await con.prepare('''update "robot" set name = $1, count_distribute = $2, wechat_no = $3, head_url = $4, qr_code = $5, update_date = now() where code = $6''')
            await update_robot_stmt.fetch(nick_name, robot_count, wechat_no, head_url, qr_code, robot_code)
    except Exception as e:
        logger.info(f'sync robot error:{e}, robot_code:{robot_code}')


async def sync_active_user_action():
    current_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    day = current_date.strftime('%Y-%m-%d')
    key = USER_OPT_DAY_REDIS_KEY.format(today=day)
    users_act = await redis.conn.hgetall(key)
    tasks = []
    logger.info(f'sync active user counts: {len(users_act)}')
    for user_id, actions in users_act.items():
        tasks.append(batch_update_active_user_operate(user_id, actions, UserOpt.ACTIVE, current_date))
    await asyncio.gather(*tasks)
    await redis.conn.expire(key, 0)


async def delete_one_star_groups():
    """
    定时移除一星群
    1. 违法群
    2. 判断一星群是否超过阈值
    3. 投放开关关闭的一星群
    4. 无点击群
    5. 人数少的群
    6. 删除到阈值
    """

    async def illegal_groups():
        """违法群"""
        async with db.conn.acquire() as con:
            illegal_groups_stmt = await con.prepare('''select id::varchar from "group" where status <> 3 and name similar to $1''')
            return records_to_value_list(await illegal_groups_stmt.fetch(settings['ILLEGAL_GROUP_NAME']), 'id')

    async def launch_switch_off_groups():
        """投放开关关闭的一星群"""
        async with db.conn.acquire() as con:
            launch_switch_off_stmt = await con.prepare('''select id from "group" where status <> 3 and quality_level = 1 and launch_switch = 0 order by create_date asc''')
            return records_to_value_list(await launch_switch_off_stmt.fetch(), 'id')

    async def no_click_groups():
        """无点击群"""
        redis_key = NO_CLICK_GROUPS_REDIS_KEY.format(today=today())
        group_codes_value = await redis.conn.get(redis_key)
        if group_codes_value:
            group_codes = ujson.loads(group_codes_value)
            async with db.conn.acquire() as con:
                get_group_stmt = await con.prepare('''select id from "group" where status <> 3 and quality_level = 1 and code = any($1) order by create_date asc''')
                return records_to_value_list(await get_group_stmt.fetch(group_codes), 'id')
        else:
            return []

    async def one_star_mem_count_limit_groups():
        """群人数小于一定人数"""
        async with db.conn.acquire() as con:
            mem_count_limit_groups_stmt = await con.prepare('''select id from "group" where status <> 3 and mem_count > 0 and mem_count <= $1 and (quality_level is null or quality_level = 1) order by create_date asc''')
            return records_to_value_list(await mem_count_limit_groups_stmt.fetch(settings['ONE_STAR_MEM_COUNT_LIMIT']), 'id')

    async def one_star_count_limit_groups():
        """一星群以及未评星群是否超过阀值"""
        async with db.conn.acquire() as con:
            mem_count_limit_groups_stmt = await con.prepare('''select count(1) from "group" where status <> 3 and (quality_level is null or quality_level = 1)''')
            one_star_count = await mem_count_limit_groups_stmt.fetchval()
        one_star_group_total_count_limit = settings['ONE_STAR_GROUP_TOTAL_COUNT_LIMIT']
        if one_star_count > one_star_group_total_count_limit:
            return True, (one_star_count - one_star_group_total_count_limit)
        return False, 0

    async def one_star_extra_limit_groups(limit_size):
        """获取要额外注销的一星群列表"""
        async with db.conn.acquire() as con:
            groups_stmt = await con.prepare('''select id from "group" where status <> 3 and quality_level = 1 order by create_date asc limit $1''')
            return records_to_value_list(await groups_stmt.fetch(limit_size), 'id')

    logger.info(f'time delete one star groups start!')
    illegal_group_ids = await illegal_groups()
    logger.info(f'illegal star group count:{len(illegal_group_ids)}')
    await inner_delete_groups(group_ids=illegal_group_ids)
    await asyncio.sleep(3)
    limit, limit_count = await one_star_count_limit_groups()  # limit_count为要注销的群总量
    if not limit:
        logger.info(f'one star group less than limit')
    else:
        logger.info(f'one star group more than limit count:{limit_count}')
        launch_switch_off_group_ids = await launch_switch_off_groups()
        launch_switch_off_group_count = len(launch_switch_off_group_ids)
        logger.info(f'launch switch off group count: {launch_switch_off_group_count}')
        if limit_count <= launch_switch_off_group_count:
            launch_switch_off_group_ids = launch_switch_off_group_ids[:limit_count]
            await inner_delete_groups(launch_switch_off_group_ids)
        else:
            await inner_delete_groups(launch_switch_off_group_ids)
            await asyncio.sleep(3)
            extra_delete_count = limit_count - launch_switch_off_group_count
            no_click_group_ids = await no_click_groups()
            no_click_group_count = len(no_click_group_ids)
            logger.info(f'no click group count:{no_click_group_count}')
            logger.debug(f'no click groups:{no_click_group_ids}')
            if extra_delete_count <= no_click_group_count:
                no_click_group_ids = no_click_group_ids[:extra_delete_count]
                await inner_delete_groups(no_click_group_ids)
            else:
                await inner_delete_groups(no_click_group_ids)
                await asyncio.sleep(3)
                one_star_delete_count = extra_delete_count - no_click_group_count  # 额外要注销的一星群
                mem_count_groups = await one_star_mem_count_limit_groups()
                mem_count_groups_count = len(mem_count_groups)
                logger.info(f'mem count less than five group count:{mem_count_groups_count}')
                if one_star_delete_count <= mem_count_groups_count:
                    mem_count_groups = mem_count_groups[:one_star_delete_count]
                    logger.debug(f'mem count groups:{mem_count_groups}')
                    await inner_delete_groups(mem_count_groups)
                else:
                    await inner_delete_groups(mem_count_groups)
                    await asyncio.sleep(3)
                    one_star_extra_count = one_star_delete_count - mem_count_groups_count
                    one_star_extra_delete_groups = await one_star_extra_limit_groups(one_star_extra_count)
                    logger.info(f'one star extra group count:{len(one_star_extra_delete_groups)}')
                    logger.debug(f'extra groups:{one_star_extra_delete_groups}')
                    await inner_delete_groups(one_star_extra_delete_groups)

    logger.info(f'time delete one star groups end!')


async def delete_two_star_groups():
    """
    定时移除二星群
    1. 判断二星群是否超过阈值
    2. 删除到阈值
    """

    async def two_star_count_limit_groups():
        """二星群是否超过阀值"""
        async with db.conn.acquire() as con:
            mem_count_limit_groups_stmt = await con.prepare('''select count(1) from "group" where status <> 3 and quality_level = 2''')
            one_star_count = await mem_count_limit_groups_stmt.fetchval()
        two_star_group_total_count_limit = settings['TWO_STAR_GROUP_TOTAL_COUNT_LIMIT']
        if one_star_count > two_star_group_total_count_limit:
            return True, (one_star_count - two_star_group_total_count_limit)
        return False, 0

    async def two_star_extra_limit_groups(limit_size):
        """获取要额外注销的二星群列表"""
        async with db.conn.acquire() as con:
            groups_stmt = await con.prepare('''select id from "group" where status <> 3 and quality_level = 2 order by create_date asc limit $1''')
            return records_to_value_list(await groups_stmt.fetch(limit_size), 'id')

    logger.info(f'time delete two star groups start!')
    limit, limit_count = await two_star_count_limit_groups()
    delete_group_ids = []  # 需要被注销的群列表
    if not limit:
        logger.info(f'two star group less than limit')
        return
    else:
        logger.info(f'one star group more than limit count:{limit_count}')
        one_star_extra_delete_groups = await two_star_extra_limit_groups(limit_count)
        delete_group_ids.extend(one_star_extra_delete_groups)

    logger.info(f'task delete two star group total count:{len(delete_group_ids)}')
    await inner_delete_groups(delete_group_ids)


if __name__ == '__main__':
    logger.info('scheduler start...')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_connect(loop))
    # asyncio.run_coroutine_threadsafe(monitor_redis_key_expire(), loop)
    scheduler._eventloop = loop
    scheduler.add_job(deal_user_withdraw_task, **job_settings[deal_user_withdraw_task.__name__])
    # 消息统计昨日数据，必须在0点之后统计
    scheduler.add_job(yesterday_group_chat_volume_task, **job_settings[yesterday_group_chat_volume_task.__name__])
    scheduler.add_job(users_groups_settlement, **job_settings[users_groups_settlement.__name__])
    scheduler.add_job(user_remind, **job_settings[user_remind.__name__])
    scheduler.add_job(monitor_task_message, **job_settings[monitor_task_message.__name__])
    scheduler.add_job(notice_group_star_yesterday_night, **job_settings[notice_group_star_yesterday_night.__name__])
    scheduler.add_job(sync_robot_info, **job_settings[sync_robot_info.__name__])
    # 活跃用户统计昨日数据，必须在0点之后统计
    scheduler.add_job(sync_active_user_action, **job_settings[sync_active_user_action.__name__])
    scheduler.add_job(delete_one_star_groups, **job_settings[delete_one_star_groups.__name__])
    scheduler.add_job(delete_two_star_groups, **job_settings[delete_two_star_groups.__name__])
    scheduler.start()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('scheduler stop...')
        loop.run_until_complete(cancel_connect(loop))
        loop.close()
