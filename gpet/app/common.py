import datetime
import math
import operator
import random
import ujson
from decimal import Decimal

from sanic.log import logger

from app import db, redis
from app.route_requests import cancel_group
from config import settings
from ut.constants import SNAPSHOT_KEY_REDIS_KEY, DISTRIBUTE_KEY_REDIS_KEY, UserOpt, USER_OPT_DAY_REDIS_KEY
from ut.utils import acquire_lock, release_lock, today

DISTRIBUTE_AMOUNT = settings['DISTRIBUTE_AMOUNT']
DISTRIBUTE_CONFIG = settings['DISTRIBUTE_CONFIG']
DISPLAY_RATE = settings['DISPLAY_RATE']     # 机器人展示比率

INCOME_TYPE = 1              # 收入
PAYMENT_TYPE = 2             # 支出
KEY_TIMEOUT = 2 * 24 * 3600  # 分配机器人缓存失效时间


# ======= 账号公用方法相关 ======= #

async def update_user_income(account_id, user_income, balance_type=INCOME_TYPE,
                             remark=None, groups=None, settle_date=None):
    '''
    账户结算完成进行账户加钱、减钱、创建流水操作
    :param account_id: 账户ID
    :param user_income: 操作金额
    :param balance_type: 操作类型 1收入 2支出
    :param remark: 备注
    :param groups: 针对的群
    :param settle_date: 结算时间
    :return:
    '''
    try:
        amount = Decimal(str(math.floor(user_income['amount'] * 100) / 100))
        if balance_type == INCOME_TYPE:
            add_amount = amount
        elif balance_type == PAYMENT_TYPE:
            add_amount = -amount
        else:
            raise TypeError(f'cannot receiver type: balance_type={balance_type}')
        if settle_date is None:
            settle_date = datetime.datetime.now().date()
        elif not isinstance(settle_date,  datetime.date):
            raise TypeError(f'settle date need date type')
        async with db.conn.acquire() as con:
            async with con.transaction():
                select_stmt = await con.prepare('select balance_amount from "account" where id=$1 for update')
                origin_amount = await select_stmt.fetchval(account_id)
                slip_stmt = await con.prepare(
                    '''insert into "account_slip" (id, account_id, balance_type, change_amount, balance, amount_type, 
                       remark, group_profit, settle_date, status) values (uuid_generate_v4(), $1, $2, $3, $4, $5, $6, $7, $8, 1)''')
                await slip_stmt.fetchrow(account_id, balance_type, amount, origin_amount + add_amount,
                                         user_income['type'], remark, ujson.dumps(groups) if groups else groups, settle_date)
                account_stmt = await con.prepare(
                    '''update "account" set balance_amount=balance_amount+$1, cumulative_income=cumulative_income+$2, 
                       update_date=now() where id=$3 returning id, balance_amount''')
                await account_stmt.fetchrow(add_amount, add_amount, account_id)
        logger.info(f'''account [{account_id}], counts: [{len(groups) if groups else 0}], 
                        type: [{user_income["type"]}], money: [{amount}]''')
    except Exception as e:
        logger.error(f'account {account_id} settle user income: [{user_income}], occur error: {e}')


# ======== 群相关 ========== #

async def currency_delete_group(group_id, cancel_reason):
    """
    删除群、注销群
    :param group_id: 群id
    :param cancel_reason: 注销原因 1-违法群 2-投放较差 3-机器人退群 4-系统主动注销 5-低星级超过限制 6-机器人封号
    :return: True: 注销成功 False: 注销失败
    """
    try:
        async with db.conn.acquire() as con:
            select_group = await con.prepare('''select "robot_group_map".id::varchar , "group".code as group_code, 
            "robot_group_map".robot_id, "robot".code as robot_code from "group" left join "robot_group_map" on 
            "robot_group_map".group_id = "group".id left join "robot" on "robot".id = "robot_group_map".robot_id 
            where "group".id =$1 and "group".status !=3''')
            group_info = await select_group.fetchrow(group_id)
        if group_info is None:
            return False

        """删除群"""
        params = {
            'robot_id': group_info['robot_code'],
            'group_id': group_info['group_code'],
            'reason': str(cancel_reason)
        }
        logger.info(f'cancel_group params, {params}')
        response = await cancel_group(params)
        logger.info(f'currency_delete_group, {response}')
        return True
    except Exception as e:
        logger.info(f'delete group error:{e}, group_id:{group_id}')
        return False


# ======= 单表查询 ======= #

async def is_key_exists(key):
    '''缓存是否存在指定的key'''
    return await redis.conn.exists(key)


async def get_account_info(user_id):
    '''查询账户信息'''
    async with db.conn.acquire() as con:
        account_stmt = await con.prepare('select * from "account" where user_id=$1 and status<>3')
        account = await account_stmt.fetchrow(user_id)
    return account


async def get_group_info(group_code):
    """根据group_code 查询group_id"""
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select * from "group" where code=$1 and status<>3''')
        group = await select_stmt.fetchrow(group_code)
        return group


async def get_user_by_code(mem_code):
    '''获取用户信息'''
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            'select * from "user" where code = $1 and status <> 3')
        user = await select_stmt.fetchrow(mem_code)
    return user


async def get_user_by_id(user_id):
    '''获取用户信息'''
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            'select * from "user" where id = $1 and status <> 3')
        user = await select_stmt.fetchrow(user_id)
    return user


async def get_robot_by_code(code):
    '''通过机器人code查询机器人信息'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            'select * from "robot" where code = $1 and status <> 3')
        robot = await st.fetchrow(code)
    return robot


async def get_robot_by_id(id):
    '''通过机器人id查询机器人信息'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            'select * from "robot" where id = $1 and status <> 3')
        robot = await st.fetchrow(id)
    return robot


async def check_exists_master_group(mem_code):
    '''查询当前用户是否存在群主群'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select u.id from "group" g join "user" u on g.user_id=u.id
               where u.code=$1 and u.code=g.owner_user_code and g.status<>3 limit 1''')
        count = await st.fetchval(mem_code)
    if not count:
        return False
    return True


async def complete_user_robot_info(user_id, robot_code):
    robot = await get_robot_by_code(robot_code)
    if not robot: return
    async with db.conn.acquire() as con:
        st = await con.prepare('''select id from "robot_add_friend" where robot_id=$1 and user_id=$2 and status <> 3''')
        if not await st.fetchrow(robot['id'], user_id):
            it = await con.prepare(
                '''insert into robot_add_friend (id, robot_id, user_id) values (uuid_generate_v4(), $1, $2)''')
            await it.fetchrow(robot['id'], user_id)


async def user_robot_info(user_id, robot_code):
    '''用户加机器人为好友的记录'''
    await complete_user_robot_info(user_id, robot_code)
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select "robot".id, "robot".code from "robot_add_friend" 
               join "robot" on "robot".id="robot_add_friend".robot_id
               where "robot_add_friend".user_id=$1 and "robot".status <> 3''')
        data = await st.fetch(user_id)
    return data


async def check_robot_distribute_record(user_id, robot_id):
    '''检查当前机器人是否分配给到当前用户'''
    async with db.conn.acquire() as con:
        st = await con.prepare('''select * from "robot_distribute" where user_id=$1 and robot_id=$2 and status <> 3''')
        data = await st.fetchrow(user_id, robot_id)
    return data


async def get_lasted_distribute_robot(user_id):
    '''查询当前用户最后一次的分配记录'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select "robot_distribute".robot_id from "robot_distribute" 
               join "robot" on "robot_distribute".robot_id="robot".id 
               where "robot_distribute".user_id=$1 and "robot".status<>3 
               order by "robot_distribute".create_date desc limit 1''')
        robot_id = await st.fetchval(user_id)
    return robot_id


async def complete_robot_distribute_record(user_id, mem_code, robot_id):
    '''补全分配记录'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''insert into "robot_distribute" (id, robot_id, user_id, user_code) 
               values (uuid_generate_v4(), $1, $2, $3)''')
        data = await st.fetchrow(robot_id, user_id, mem_code)
    return data


# ======== 机器人相关 ========== #

async def check_robot_amount_distribute(user_id, mem_code, channel, robot_code=None):
    """
    分配机器人逻辑: 用户加的机器人好友优先分配，其次随机分配机器人
    :param user_id: 用户id
    :param mem_code: 用户code
    :param channel: 用户对应的渠道
    :param robot_code: 优先分配当前的机器人code
    :return: (boolean, robot_id): 是否是当前优先分配的机器人，机器人id
    """
    user_robots = await user_robot_info(user_id, robot_code)
    if not user_robots:     # 用户没有加机器人好友记录
        logger.warning(f'not match user: {user_id} add robot friend records')
        robot_id = await random_robot_distribute(user_id, mem_code, channel)
        return False, str(robot_id) if robot_id else None
    robot_ids = [str(robot['id']) for robot in user_robots]
    robots_amount = await check_robots_amount(robot_ids)
    logger.debug(f'get current user: {user_id}, robots amount: {robots_amount}')
    if not robots_amount:   # 用户加的机器人好友都没有可用额度
        logger.warning(f'not match user: {user_id} robots amount')
        robot_id = await random_robot_distribute(user_id, mem_code, channel)
        return False, str(robot_id) if robot_id else None
    if not robot_code:
        robot_id = max(robots_amount.items(), key=operator.itemgetter(1))[0]
        return False, str(robot_id)
    current_robot = await get_robot_by_code(robot_code)
    if current_robot and int(robots_amount.get(str(current_robot['id']), 0)) > 0:  # 检测当前机器人是否存在可用额度
        logger.debug(f'distribute current robot: {str(current_robot["id"])}')
        return True, str(current_robot['id'])
    else:                   # 推送用户加的其他机器人记录
        robot_id = max(robots_amount.items(), key=operator.itemgetter(1))[0]
        return False, str(robot_id)


async def check_robots_amount(robot_ids):
    '''查询一批机器人的剩余额度'''
    await init_cache_if_not_exists()
    results = {}
    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    for robot_id in robot_ids:
        robot_overage = await redis.conn.zscore(distribute_key, robot_id)
        if robot_overage and int(robot_overage) >= 1:
            results.update({robot_id: robot_overage})
    return results


async def random_robot_distribute(user_id, mem_code, channel):
    '''优先最后分配的机器人查询，其次分配其他机器人'''
    dist_robot_id = await get_lasted_distribute_robot(user_id)
    robot_id = await robot_distribution(robot_id=dist_robot_id, channel=channel)
    if robot_id and not await check_robot_distribute_record(user_id, robot_id):
        await complete_robot_distribute_record(user_id, mem_code, robot_id)
    return robot_id


async def init_cache_if_not_exists():
    key = SNAPSHOT_KEY_REDIS_KEY.format(today=today())
    if not await is_key_exists(key):
        lock_name = 'robot_snapshot'
        lock_value = await acquire_lock(lock_name, acquire_timeout=3)
        if lock_value and not await is_key_exists(key):
            await _robot_snapshot()
            await release_lock(lock_name, lock_value)
        else:   # 目前3秒未同步到缓存的用户返回404
            logger.info('acquire lock timeout, user need try againt')
            pass


async def robot_distribution(robot_id=None, count=1, channel=None):
    '''
    概念：
        额度=机器人00:00时剩余可激活群数量
        当日最大次数=min（15，额度）*3
        激活次数=当日机器人激活群数，次日清零。
        展示次数=该机器人当天在领养页面展示给过多少个不同的用户（UV）
    展示逻辑：
        random（max（当日最大次数/3-激活次数））
        展示次数=当日最大次数或（当日最大次数/3-激活次数）=0时，该机器人退出展示范围
    保底：
        激活机器人最后一个额度（即机器人第30个群激活成功时）的用户，机器人会主动给该用户推送与展示相同逻辑得出的机器人；
        激活机器人当天第15个额度的用户（激活次数=15），机器人会主动给该用户推送与展示相同逻辑得出的机器人；
        其他用户均发起激活请求时，机器人才被动给该用户推送与展示相同逻辑得出的机器人
    '''
    await init_cache_if_not_exists()
    # key = SNAPSHOT_KEY_REDIS_KEY.format(today=today())
    # if not await is_key_exists(key):
    #     lock_name = 'robot_snapshot'
    #     lock_value = await acquire_lock(lock_name, acquire_timeout=3)
    #     if lock_value and not await is_key_exists(key):
    #         await _robot_snapshot()
    #         await release_lock(lock_name, lock_value)
    #     else:   # 目前3秒未同步到缓存的用户返回404
    #         logger.info('acquire lock timeout, user need try againt')
    #         pass
    robot_id = await _specific_robot_distribution(robot_id=robot_id, count=count)
    if not robot_id:
        robot_id = await _random_robot_distribution(count, channel)
    return robot_id


async def remove_robot_distribute(robot_id):
    '''将机器人置为不可分配'''
    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    await redis.conn.zrem(distribute_key, robot_id)
    logger.info(f'remove_robot_distribute --> [{robot_id}]')


async def _robot_snapshot():
    '''机器人表中剩余可激活群数快照'''
    count = DISTRIBUTE_AMOUNT * DISTRIBUTE_CONFIG
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            '''select id::varchar, 
                 case when (count_threshold - count_distribute) > $1 
                 then $2 else (count_threshold - count_distribute) end as count_overage
               from "robot" where (count_threshold - count_distribute) > 0 and status = 1''')
        robots = await select_stmt.fetch(count, count)
    if not robots:
        return
    await _zadd_cache(robots)


async def _zadd_cache(robots):
    snapshot_key = SNAPSHOT_KEY_REDIS_KEY.format(today=today())
    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    snapshot_results = {}
    distribute_results = {}
    for robot in robots:
        snapshot_results[robot['id']] = robot['count_overage'] * DISPLAY_RATE
        distribute_results[robot['id']] = robot['count_overage']
    async with await redis.conn.pipeline() as pipe:
        await pipe.zadd(snapshot_key, **snapshot_results)
        await pipe.zadd(distribute_key, **distribute_results)
        await pipe.expire(snapshot_key, KEY_TIMEOUT)
        await pipe.expire(distribute_key, KEY_TIMEOUT)
        await pipe.execute()
    logger.info(f'cache init success!!!')


async def _get_max_score(key, count):
    max_score_list = await redis.conn.zrevrange(key, 0, 0, withscores=True, score_cast_func=int)
    if not max_score_list:
        return None
    else:
        _, max_score = max_score_list[0]
        if max_score < count:
            return None
        return max_score


async def _choose_robot_id(key, max_score, channel):
    for score in list(range(max_score, 0, -1)):
        suit_robot_ids = await _get_suit_robot_ids(key, score, channel=channel)
        if suit_robot_ids:
            return random.choice(suit_robot_ids)


async def _get_suit_robot_ids(key, score, channel=None):
    suit_robot_ids = []
    robot_ids = await redis.conn.zrangebyscore(key, score, score)
    async with db.conn.acquire() as con:
        if channel is None:
            select_stmt = await con.prepare('''select id from "robot" where channel is null and id = any($1)''')
            suit_robots = await select_stmt.fetch(list(robot_ids))
        else:
            select_stmt = await con.prepare('''select id from "robot" where channel=$1 and id = any($2)''')
            suit_robots = await select_stmt.fetch(channel, list(robot_ids))
    for robot in suit_robots:
        suit_robot_ids.append(robot['id'])
    return suit_robot_ids


async def _specific_robot_distribution(robot_id=None, count=1):
    '''指定机器人额度查询与分配'''
    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    robot_overage = await redis.conn.zscore(distribute_key, robot_id)
    if robot_overage and int(robot_overage) >= count:
        return robot_id


async def _random_robot_distribution(count, channel=None):
    '''随机分配一个机器人'''
    distribute_key = DISTRIBUTE_KEY_REDIS_KEY.format(today=today())
    max_score = await _get_max_score(distribute_key, count)
    if not max_score:
        return None
    robot_id = await _choose_robot_id(distribute_key, max_score, channel=channel)
    if channel is not None and not robot_id:
        robot_id = await _choose_robot_id(distribute_key, max_score, channel=None)
    return robot_id

# ========= 用户操作相关 ========= #


async def get_user_act(user_id, act_type, day=None):
    '''查询指定用户操作记录'''
    if day is None:
        day = datetime.datetime.now().date()
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select user_id::varchar, type, to_char(day, 'YYYY-MM-DD') as day 
               from "operation_record" where user_id=$1 and type=$2 and day=$3''')
        user_act = await st.fetchrow(user_id, act_type, day)
    return user_act


async def init_user_act(user_id, act_type, detail=None, day=None):
    ''' 初始化user操作记录 '''
    if detail is not None and not isinstance(detail, str):
        raise TypeError(f'{detail} is not json or str type!')
    if day is None:
        day = datetime.datetime.now().date()
    async with db.conn.acquire() as con:
        it = await con.prepare(
            'insert into "operation_record" (user_id, type, detail, day) values ($1, $2, $3, $4)')
        user_act = await it.fetch(user_id, act_type, detail, day)
    return user_act


async def batch_update_active_user_operate(user_id, actions, act_type, day):
    '''批量更新活跃用户操作记录'''
    try:
        async with db.conn.acquire() as con:
            up = await con.prepare(
                '''update "operation_record" set detail = $1 where user_id=$2 and type=$3 and day=$4''')
            user_act = await up.fetch(actions, user_id, act_type, day)
            return user_act
    except Exception as e:
        logger.error(f'update user: {user_id} actions: {actions} type: {act_type} error: {e}')


async def add_active_user_operate(user_id, act_type, trigger, day=None):
    '''更新活跃用户每次的操作记录'''
    if day is None:
        day = datetime.datetime.now().date()
    async with db.conn.acquire() as con:
        up = await con.prepare(
            '''update "operation_record" set 
               detail = jsonb_set(detail, $1, (coalesce(detail -> $2, '0')::int+1)::text::jsonb)
               where user_id=$3 and type=$4 and day=$5''')
        user_act = await up.fetch({trigger}, trigger, user_id, act_type, day)
        return user_act


async def active_user_operate(user_id, trigger):
    '''活跃用户操作入口'''
    if trigger not in ['access_web_counts', 'chat_counts']:
        raise ValueError(f'not support this key trigger: {trigger}')
    day = datetime.datetime.now().date().strftime('%Y-%m-%d')
    key = USER_OPT_DAY_REDIS_KEY.format(today=day)
    signle_user_opt = await redis.conn.hget(key, user_id)
    if not signle_user_opt:
        detail_opt = {'access_web_counts': 1 if trigger == 'access_web_counts' else 0,
                      'chat_counts': 1 if trigger == 'chat_counts' else 0}
        await redis.conn.hset(key, user_id, ujson.dumps(detail_opt))
        await init_user_act(user_id, UserOpt.ACTIVE, ujson.dumps(detail_opt))
    else:
        user_opt = ujson.loads(signle_user_opt)
        user_opt[trigger] += 1
        await redis.conn.hset(key, user_id, ujson.dumps(user_opt))
