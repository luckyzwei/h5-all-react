import asyncio
import datetime
from hashlib import md5
from itertools import groupby
from operator import itemgetter

from sanic.log import logger

from config import settings
from ut.constants import PARAMS_ERROR_CODE, COMPLETE_USER_REDIS_KEY, TYPE, DUPLICATE_REQUEST_CODE
from app import db, redis
from ut.response import response_json
from app.settlement import signle_user_groups_settlement, async_groupby
from ut.utils import records_to_list, get_page_info, records_to_value_list, str_to_date, set_lock

REDIS_TIMEOUT = 24 * 60 * 60
MD5_SECRET_KEY = settings['MD5_SECRET_KEY']


# @bp.route('/bi/users', methods=['POST'])
async def users_info(request):
    '''
    返回给BI的数据
    {
        "user_id": string,               // 用户id
        "maps": {
            "father_id": string,         // 师傅
            "grand_father_id": string    // 师爷
        },
        "groups": ["", ""]              // 群id
        }
    }
    '''
    async def get_user_relationships(user_id):
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

    async def get_user_ids(datetime, user_ids):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select "user".id as user_id, "user".code as user_code, "group".code as group_code from "user" 
                   join "group" on "user".id="group".user_id
                   where "user".status<>3 and "group".status <>3 and "user".create_date <= to_timestamp($1, 'YYYY-MM-DD HH24:MI:SS') 
                   and "group".create_date <= to_timestamp($2, 'YYYY-MM-DD HH24:MI:SS') and "user".id=any($3) order by "user".id''')
            users = await st.fetch(datetime, datetime, user_ids)
        return records_to_list(users), records_to_value_list(users, 'user_code')

    async def get_user_counts(datetime):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select "user".id from "user" 
                   join "group" on "user".id="group".user_id where "user".status<>3 
                   and "group".status <>3 and "user".create_date <= to_timestamp($1, 'YYYY-MM-DD HH24:MI:SS') 
                   and "group".create_date <= to_timestamp($2, 'YYYY-MM-DD HH24:MI:SS') group by "user".id''')
            total_users = await st.fetch(datetime, datetime)
        return records_to_value_list(total_users, 'id'), len(total_users)

    async def async_groupby(users, sort_key):
        return groupby(users, key=itemgetter(sort_key))

    async def pre_next_page_count(current_page, page_size):
        return current_page * page_size, (current_page + 1) * page_size

    logger.debug(f'receiver bi data: {request.json}')
    datetime = request.json.get('datetime')
    current_page = int(request.raw_args.get('current_page'))
    page_size = int(request.raw_args.get('page_size'))
    timestamp = request.json.get('timestamp')
    sign = request.json.get('sign')
    # 数据校验
    if not all([timestamp, sign]):
        return response_json(None, code=PARAMS_ERROR_CODE)
    secret_md5 = md5()
    secret_md5.update('#'.join([timestamp, MD5_SECRET_KEY]).encode('utf-8'))
    if secret_md5.hexdigest() != sign:
        return response_json(None, code=PARAMS_ERROR_CODE)
    data = []
    static_users, user_counts = await get_user_counts(datetime)
    pre_count, next_count = await pre_next_page_count(current_page, page_size)
    page_user_ids = static_users[pre_count: next_count]
    users, user_codes = await get_user_ids(datetime, page_user_ids)
    cache_maps = {}
    if user_codes:
        maps = await redis.conn.hmget(COMPLETE_USER_REDIS_KEY, user_codes)
        for key, value in zip(user_codes, maps):
            cache_maps[key] = value
    for user_code, items in await async_groupby(users, 'user_code'):
        user_maps = cache_maps.get(user_code)
        copy_items = list(items)
        user_id = copy_items[0]['user_id']
        groups = []
        for item in copy_items:
            groups.append(item['group_code'])
        if not user_maps:
            user_maps = await get_user_relationships(user_id=user_id)
        data.append({'user_id': user_code, 'groups': groups, 'maps': user_maps})
    page_info = get_page_info(page_size, current_page, user_counts)
    return response_json(data, page_info=page_info)


# @bp.route('/settlement', methods=['POST'])
async def users_statistic_view(request):
    '''bi数据统计回传, 账户加钱、群同步
    {
        "settle_date": "",
        "timestamp": "",
        "sign": "",
        "data": {"code": "amount"}
    }
    '''
    async def need_settlement_groups(groups):
        groups_join = ','.join(groups.keys())
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select "group".id as group_id, "group".code, "user".id as user_id, "user".code as user_code
                   from "group" join "user" on "group".user_id="user".id where "group".status<>3 and 
                   exists(select tmp_code from (select unnest(string_to_array($1, ',')) as tmp_code) as tmp where tmp.tmp_code="group".code) 
                   order by "user".code''')
            data = await st.fetch(groups_join)
        return records_to_list(data)

    async def coroutine_thread_run_settle(groups, settle_date):
        settle_groups = await need_settlement_groups(groups)
        logger.info(f'need settle groups: {len(settle_groups)}')
        for user_code, items in await async_groupby(settle_groups, 'user_code'):
            copy_items = list(items)
            for item in copy_items:
                item['amount'] = groups.get(item['code'], 0)
            logger.debug(f'adv settle user code: {user_code}')
            try:
                await signle_user_groups_settlement(user_code, copy_items, settle_date, settle_type=TYPE.AD_CLICK)
            except Exception as e:
                logger.error(f'user [{user_code} settle occer error: [{e}]]')

    async def check_settle_day_exist(date):
        async with db.conn.acquire() as con:
            st = await con.prepare('select count(*) from "account_slip" where settle_date=$1 and amount_type=$2')
            count = await st.fetchval(date, TYPE.AD_CLICK)
        if count > 0:
            logger.info(f'exist settle day {date} and find count {count}')
            return True
        return False

    logger.debug(f'settlement callback data #: {request.json}')
    timestamp = request.json.get('timestamp')
    sign = request.json.get('sign')
    settlement_date = request.json.get('settle_date')
    # 数据校验
    if not all([str(timestamp), sign, settlement_date]):
        return response_json(None, code=PARAMS_ERROR_CODE)
    secret_md5 = md5()
    secret_md5.update('#'.join([timestamp, MD5_SECRET_KEY]).encode('utf-8'))
    if secret_md5.hexdigest() != sign:
        return response_json(None, code=PARAMS_ERROR_CODE)
    groups = request.json.get('data', {})
    settle_date = str_to_date(settlement_date)
    if await check_settle_day_exist(settle_date):
        logger.error(f'exist duplicate call ad click, date {settle_date}')
        return response_json(None, code=DUPLICATE_REQUEST_CODE)
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(coroutine_thread_run_settle(groups, settle_date), loop)
    return response_json(None)
