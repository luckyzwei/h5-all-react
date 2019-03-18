'''
群结算：
    - 涉及到的用户：当前用户，师傅、师爷
    - 结算规则：
        - 当日之前未结算的群
        - 导群未满30天
        - 机器人在群内
        - 老群根据重复率计算且人数大于50人
        - 新群根据星级计算
    - 主要逻辑：
        - 查询当日未结算且导群未满30天且机器人在群内的群，对群根据用户分组
        - 以用户为单位对群进行结算、账户加钱
'''
import asyncio
import functools
import math
import ujson
import datetime
from decimal import Decimal
from itertools import groupby
from operator import itemgetter

from config import settings
from ut.constants import TYPE, COMPLETE_USER_REDIS_KEY
from ut.response import dumps
from ut.utils import records_to_list, call

INCOME_TYPE = 1     # 收入
PAYMENT_TYPE = 2    # 支出
NEW_GROUP = 0       # 新群
OLD_GROUP = 1       # 老群
LEVEL_MAP = {
    0: 'zero',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five'
}

EMAIL_RECEIVERS = 'GPET:EMAIL_RECIEIVERS'

# 师傅、师爷结算比率
FATHER_SETTLE_RATE = settings['FATHER_SETTLE_RATE']
GRAND_FATHER_SETTLE_RATE = settings['GRAND_FATHER_SETTLE_RATE']
FATHER_AD_SETTLE_RATE = settings['FATHER_AD_SETTLE_RATE']
GRAND_FATHER_AD_SETTLE_RATE = settings['GRAND_FATHER_AD_SETTLE_RATE']


async def init_connect(_loop):
    await db.init_app(_loop, settings['DATABASES'])
    redis.init_app(_loop, settings['REDIS'])


async def cancel_connect(_loop):
    await db.conn.close()
    redis.conn.connection_pool.disconnect()


def yesterday_date():
    return datetime.datetime.now().date() - datetime.timedelta(days=1)


def constant_data_cache(key, name, is_dumps=True):
    '''
     针对散列缓存读取与存储装饰
    :param key: 散列缓存的key
    :param name: 散列中对应的field
    :param is_dumps: 是否对value做序列化操作
    :return: str or list or dict
    '''
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name_key = kwargs.get(name)
            data = await redis.conn.hget(key, name_key)
            if data:
                if is_dumps:
                    return ujson.loads(data)
                else:
                    return data
            else:
                resp = await call(func, *args, **kwargs)
                if not resp:
                    return resp
                if is_dumps:
                    await redis.conn.hset(key, name_key, dumps(resp))
                else:
                    await redis.conn.hset(key, name_key, resp)
                return resp
        return wrapper
    return decorator


async def update_user_income(account_id, amount_type, amount, settle_date, groups=None):
    '''
    账户结算完成进行账户加钱、减钱、创建流水操作
    :param account_id: 账户ID
    :return: 当前账户余额
    '''
    try:
        amount = Decimal(str(math.floor(amount * 100) / 100))
        if amount != 0:
            async with db.conn.acquire() as con:
                async with con.transaction():
                    select_stmt = await con.prepare('select balance_amount from "account" where id=$1 for update')
                    origin_amount = await select_stmt.fetchval(account_id)
                    slip_stmt = await con.prepare(
                        '''insert into "account_slip" (id, account_id, balance_type, change_amount, balance, amount_type, 
                           settle_date, group_profit, status) values (uuid_generate_v4(), $1, $2, $3, $4, $5, $6, $7, 1)''')
                    await slip_stmt.fetchrow(account_id, INCOME_TYPE, amount, origin_amount + amount,
                                             amount_type, settle_date, ujson.dumps(groups) if groups else groups)
                    account_stmt = await con.prepare(
                        '''update "account" set balance_amount=balance_amount+$1, cumulative_income=cumulative_income+$2, 
                        update_date=now() where id=$3 returning id, balance_amount''')
                    await account_stmt.fetchrow(amount, amount, account_id)
        if groups and amount_type == TYPE.PULL_GROUP:
            groups_task = [(update_group(group_code)) for group_code in groups]
            await asyncio.gather(*groups_task)
            logger.info(f'account: [{account_id}] counts: [{len(groups)}], type: [{amount_type}], money: [{amount}]')
        elif groups:
            logger.info(f'account: [{account_id}] counts: [{len(groups)}], type: [{amount_type}], money: [{amount}]')
        else:
            logger.error(f'account: [{account_id}] no groups, amount type: [{amount_type}], money: [{amount}]')
    except Exception as e:
        logger.error(f'update account [{account_id}] occur error: [{e}]')


async def update_group(code):
    '''更新群'''
    async with db.conn.acquire() as con:
        update_stmt = await con.prepare(
            '''with total_settle_count as (select "group_profit_template".rule -> (case "group".quality_level 
                                           when 1 then 'one' when 2 then 'two' when 3 then 'three' when 4 then 'four' 
                                           when 5 then 'five' end) -> 'day' as settle_day from "group_profit_template" 
                                           join "group" on "group_profit_template".id="group".profit_template_id
                                           where "group".code = $1 and "group".status = 1 limit 1)
               update "group" set update_date=now(), settle_count = settle_count + 1,
               status = case when (settle_count + 1 >= (select settle_day::integer from total_settle_count) and status=1) 
                        then 2 else status end
               where code = $1 and status = 1''')
        await update_stmt.fetchval(code)


async def need_settlement_groups():
    '''还需结算的群统计'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''select "user".code as user_code, "group".user_id, "group".code, "group".repeate_rate, "group".mem_count,
                      "group".quality_level, "group".old_group, "group_profit_template".rule, 
                      case when "group".owner_user_code="user".code then True else False end as master_group
               from "group" join "group_profit_template" on "group".profit_template_id="group_profit_template".id
               join "user" on "user".id="group".user_id
               where "group".status = 1 and "group".running_status = 1 and "group".settle_count < 30
               and (("group".old_group = 0 and "group".quality_level is not null) or 
                   ("group".old_group = 1 and "group".repeate_rate is not null 
                    and "group".mem_count is not null and "group".mem_count >= 50))
               and "group".create_date < timestamp 'today' order by "user".code, "group".create_date desc''')
        groups = await st.fetch()
    return groups


def profit(group, old_rate, new_rate, is_current_user):
    '''
    新老群群结算加钱策略
    rule参数: {
        "one": {"day": "", "profit": float, "rate": float, "activity_profit": float}
        "two": {"day": "", "profit": float, "rate": float, "activity_profit": float}
        "three": {"day": "", "profit": float, "rate": float, "activity_profit": float}
        "four": {"day": "", "profit": float, "rate": float, "activity_profit": float}
        "five": {"day": "", "profit": float, "rate": float, "activity_profit": float}
    }
    '''
    rule = ujson.loads(group['rule'])
    level = group['quality_level']
    is_master_group = group['master_group']
    if group['old_group'] == OLD_GROUP and group.get('repeate_rate') \
            and group.get('mem_count') and group.get('mem_count') >= 50:    # 老群：重复率存在值且人数大于等于50
        if is_master_group and is_current_user:
            logger.debug(f'use master group settle rate...')
            return old_rate * 0.45 * (1 - group['repeate_rate'])
        else:
            return old_rate * 0.1 * (1 - group['repeate_rate'])
    elif group['old_group'] == NEW_GROUP and level:                         # 新群：星级存在
        rule_map = LEVEL_MAP.get(level)
        profit = rule.get(rule_map)['profit']
        rate = rule.get(rule_map)['rate'] if rule.get(rule_map).get('rate') else 1
        if is_current_user:
            activity_profit = rule.get(rule_map).get('activity_profit', 0)
            return (activity_profit + profit) * rate * new_rate
        return profit * new_rate * rate
    else:
        return False


def apprentice_profit(group, rate):
    '''广告点击结算加钱策略'''
    return group['amount'] * rate


def settle_user_profit(group, type):
    '''当前用户加钱策略'''
    if type == TYPE.PULL_GROUP:
        return profit(group, 1, 1, True)
    elif type == TYPE.AD_CLICK:
        return apprentice_profit(group, 1)
    else:
        return 0


def settle_father_profit(group, type):
    '''当前用户师傅加钱策略'''
    if type == TYPE.PULL_GROUP:
        return profit(group, 1, FATHER_SETTLE_RATE, False)
    elif type == TYPE.AD_CLICK:
        return apprentice_profit(group, FATHER_AD_SETTLE_RATE)
    else:
        return 0


def settle_grand_father_profit(group, type):
    '''当前用户师爷加钱策略'''
    if type == TYPE.PULL_GROUP:
        return profit(group, 0.3, GRAND_FATHER_SETTLE_RATE, False)
    elif type == TYPE.AD_CLICK:
        return apprentice_profit(group, GRAND_FATHER_AD_SETTLE_RATE)
    else:
        return 0


def settle_type_value(type):
    if type == TYPE.PULL_GROUP:
        return TYPE.PULL_GROUP, TYPE.SUB_PULL_GROUP
    elif type == TYPE.AD_CLICK:
        return TYPE.AD_CLICK, TYPE.SUB_AD_CLICK


@constant_data_cache(COMPLETE_USER_REDIS_KEY, 'user_id')
async def get_user_relationships(user_id):
    '''获取用户的师傅师爷'''
    async with db.conn.acquire() as con:
        st = await con.prepare(
            '''with recursive parent as (
                 select user_id, sharing_user_id, 0 as depth from "sharing_record" where user_id=$1
               union
                 select psr.user_id, psr.sharing_user_id, depth - 1
                 from "sharing_record" psr join parent p on p.sharing_user_id=psr.user_id where p.depth > -1)
               select "user".code as code, parent.depth from parent join "user" on parent.sharing_user_id="user".id;
            ''')
        users = await st.fetch(user_id)
    results = {'grand_father_id': None}
    for user in users:
        if user['depth'] == 0:
            results.update({'father_id': user['code']})
        elif user['depth'] == -1:
            results.update({'grand_father_id': user['code']})
    if len(results) == 1 and not results.get('grand_father_id'):
        results = None
    return results


# @constant_data_cache(USER_CODE_ID_MAP_REDIS_KEY, 'user_code', is_dumps=False)
async def get_user_id(user_code):
    async with db.conn.acquire() as con:
        st = await con.prepare('select id from "user" where code=$1')
        user_id = await st.fetchval(user_code)
    return user_id


# @constant_data_cache(USER_ACCOUNT_REDIS_KEY, 'user_code', is_dumps=False)
async def user_account(user_code):
    '''获取用户的账户id'''
    async with db.conn.acquire() as con:
        account_stmt = await con.prepare(
            '''select "account".id::varchar from "account" 
               join "user" on "account".user_id="user".id where "user".code=$1''')
        account_id = await account_stmt.fetchval(user_code)
    return account_id


async def async_groupby(data, sort_key):
    return groupby(data, key=itemgetter(sort_key))


async def signle_user_groups_settlement(user_code, items, settle_date, settle_type):
    '''
    单个用户及其师傅师爷结算
    :param user_code: 用户code
    :param items: 用户对应的群信息
    :param settle_type: 1-群结算 2-广告结算
    :return:
    '''
    user_profit = Decimal()
    fh_user_profit = Decimal()
    grfh_user_profit = Decimal()
    user_groups_profit = {}
    fh_groups_profit = {}
    grfh_groups_profit = {}
    fh_account_id = False
    grfh_account_id = False
    user_id = items[0]['user_id']
    user_rel = await get_user_relationships(user_id=user_id)
    user_account_id = await user_account(user_code=user_code)
    if not user_account_id:
        logger.error(f'not match user {user_id} account, this an error')
    if user_rel:
        fh_code = user_rel.get('father_id')
        grfh_code = user_rel.get('grand_father_id')
        if fh_code:
            fh_account_id = await user_account(user_code=fh_code)
        else:
            logger.error(f'not match user\'s: {user_id} father code')
        if grfh_code:
            grfh_account_id = await user_account(user_code=grfh_code)

    for group in items:
        profit = settle_user_profit(group, type=settle_type)
        if profit:
            user_profit += Decimal(str(profit))
        user_groups_profit.update({group['code']: profit})
        fh_profit = settle_father_profit(group, type=settle_type)
        if fh_profit:
            fh_user_profit += Decimal(str(fh_profit))
        fh_groups_profit.update({group['code']: fh_profit})
        grfh_profit = settle_grand_father_profit(group, type=settle_type)
        if grfh_profit:
            grfh_user_profit += Decimal(str(grfh_profit))
        grfh_groups_profit.update({group['code']: grfh_profit})
    tasks = []
    user_type, apprentice_type = settle_type_value(settle_type)
    if user_account_id:
        tasks.append(update_user_income(user_account_id, user_type, user_profit, settle_date, user_groups_profit))
    if fh_account_id and fh_user_profit != 0:
        tasks.append(update_user_income(fh_account_id, apprentice_type, fh_user_profit, settle_date, fh_groups_profit))
    if grfh_account_id and grfh_user_profit != 0:
        tasks.append(update_user_income(grfh_account_id, apprentice_type, grfh_user_profit, settle_date, grfh_groups_profit))
    await asyncio.gather(*tasks)


async def users_groups_settlement():
    '''用户群结算统计'''
    logger.info('start user groups settled...')
    settle_groups = records_to_list(await need_settlement_groups())
    logger.info(f'need settlement groups count: {len(settle_groups)}')
    index = 0
    settle_date = yesterday_date()
    for user_code, items in await async_groupby(settle_groups, 'user_code'):
        index += 1
        copy_items = list(items)
        try:
            await signle_user_groups_settlement(user_code, copy_items, settle_date, settle_type=TYPE.PULL_GROUP)
        except Exception as e:
            logger.error(f'user [{user_code} settle occer error: [{e}]]')
    logger.info(f'include users count: {index}')


from schedule_tasks import logger, db, redis