import ujson
from datetime import datetime

from sanic.log import logger
from sanic_jwt import protected
from sanic_jwt.decorators import inject_user

from app import db, redis
from ut.utils import aly_text_check
from ut.response import response_json
from ut.utils import records_to_list, str_to_datetime, get_page_info
from ut.constants import RESOURCE_NOT_FOUND_CODE, PARAMS_ERROR_CODE, SENSITIVE_WORD_CODE, \
    CREATED_FAILED_CODE, EXISTS_SAME_TIME_CREATED_CODE, TASK_MSG_MONITOR_REDIS_KEY, \
    MASS_MSG_TASK_CREATE_REDIS_KEY

# 发送状态
NOT_SEND_MSG = 0    # 信息补全成功但未发送
SEND_SUCCESS = 2    # 信息发送成功
FAIL_DELETE = 3     # 失效
MAX_MASS_MSG_AMOUNT = 2     # 每日最大创建次数


# @bp.route('/tasks/<task_id:[a-zA-Z0-9\\-]+>')
@protected()
@inject_user()
async def enter_mass_task_view(request, task_id, *args, **kwargs):
    '''进入群发消息'''
    async def is_completion(task_id):
        task_content = await redis.conn.get(MASS_MSG_TASK_CREATE_REDIS_KEY.format(task_id=task_id))
        return task_content

    task_content = await is_completion(task_id)
    if task_content:
        return response_json(dict({'id': task_id, 'content': ujson.loads(task_content)}))
    return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='信息已补全或失效')


# @bp.route('/tasks/<task_id:[a-zA-Z0-9\\-]+>', methods=['PUT'])
@protected()
@inject_user()
async def completion_task_view(request, task_id, *args, **kwargs):
    '''补全群发消息'''
    async def check_can_created_today(user_id, send_date):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select to_char(send_date, 'YYYY-MM-DD') as day, count(1) as count from "group_task" 
                   where user_id=$1 and status<>$2 and type = 1 group by to_char(send_date, 'YYYY-MM-DD')''')
            day_group_count = records_to_list(await st.fetch(user_id, FAIL_DELETE))
        date = str_to_datetime(send_date)
        if date <= datetime.now():
            return False
        str_date = date.strftime('%Y-%m-%d')
        for item in day_group_count:
            if item['day'] == str_date and item['count'] >= MAX_MASS_MSG_AMOUNT:
                logger.info(f'user [{user_id}] create mass msg max day [{str_date}]')
                return False
        return True

    async def check_group_same_time_created(send_date, group_ids):
        date = str_to_datetime(send_date)
        str_date_minute = date.strftime('%Y-%m-%d %H:%M')
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select count(1) from "group_task" 
                   where to_char(send_date, 'YYYY-MM-DD HH24:MI') = $1 and status<>3 and type = 1 and group_ids ?| $2''')
            count = await st.fetchval(str_date_minute, group_ids)
        if count > 0:
            return False
        return True

    async def combine_content(message):
        '''组合消息'''
        task_content = await redis.conn.get(MASS_MSG_TASK_CREATE_REDIS_KEY.format(task_id=task_id))
        if not task_content:
            return None
        content = ujson.loads(task_content)
        content.append(message)
        return content

    async def save_task(id, content, group_ids, user_id, send_date):
        async with db.conn.acquire() as con:
            task_stmt = await con.prepare(
                '''insert into "group_task" (id, user_id, group_ids, content, status, send_date, type)
                   values ($1, $2, $3, $4, $5, to_timestamp($6, 'YYYY-MM-DD HH24:MI:SS'), 1)''')
            await task_stmt.fetchval(id, user_id, group_ids, content, NOT_SEND_MSG, send_date)
        await redis.conn.expire(MASS_MSG_TASK_CREATE_REDIS_KEY.format(task_id=id), 0)

    async def create_redis_task(id, send_date):
        '''创建群发缓存'''
        timestamp = int(send_date.timestamp())
        await redis.conn.zadd(TASK_MSG_MONITOR_REDIS_KEY, timestamp, id)

    user_id = kwargs['user']['user_id']
    message = request.json.get('message')
    group_ids = request.json.get('group_ids')
    send_date = request.json.get('send_date')
    if not all([message, group_ids, send_date]):
        return response_json(None, code=PARAMS_ERROR_CODE, msg='缺少必要的参数')
    if not await check_can_created_today(user_id, send_date):
        return response_json(None, code=CREATED_FAILED_CODE, msg='达到当日最大创建次数')
    if not await check_group_same_time_created(send_date, group_ids):
        return response_json(None, code=EXISTS_SAME_TIME_CREATED_CODE, msg='同一群存在相同的发送时间')
    if not await aly_text_check(message['content']):
        return response_json(None, code=SENSITIVE_WORD_CODE, msg='检测到敏感词汇')
    content = await combine_content(message)
    if not content:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='群发消息已过期')
    content = ujson.dumps(content)
    group_ids = ujson.dumps(group_ids)
    await save_task(task_id, content, group_ids, user_id, send_date)
    send_date = str_to_datetime(send_date)
    await create_redis_task(task_id, send_date)
    return response_json(None)


# @bp.route('/tasks/messages')
@protected()
@inject_user()
async def mass_message_task_view(request, user):
    '''群发消息页面'''
    async def mass_message_data(direction, current_page, page_size):
        async with db.conn.acquire() as con:
            if direction == 'up':
                st = await con.prepare(
                    '''select to_char(send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date, 
                       jsonb_array_length(group_ids)::int as group_counts, status, id
                       from "group_task" where user_id=$1 and status <> $2 and type=1
                       and send_date >= timestamp 'today' and send_date <= (current_date + interval '3' day) 
                       order by send_date desc limit $3 offset $4''')
                st_count = await con.prepare('''select count(1) from "group_task" where user_id=$1 and status <> $2 and type=1
                       and send_date >= timestamp 'today' and send_date < (current_date + interval '3' day)''')
            else:
                st = await con.prepare(
                    '''select to_char(send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date, 
                       jsonb_array_length(group_ids)::int as group_counts, status, id
                       from "group_task" where user_id=$1 and status <> $2 and type=1
                       and send_date < timestamp 'today' and send_date >= (current_date - interval '3' day)
                       order by send_date desc limit $3 offset $4''')
                st_count = await con.prepare('''select count(1) from "group_task" where user_id=$1 and status <> $2 and type=1
                       and send_date < timestamp 'today' and send_date >= (current_date - interval '3' day)''')
            count = await st_count.fetchval(user['user_id'], FAIL_DELETE)
            datas = await st.fetch(user['user_id'], FAIL_DELETE, page_size, current_page * page_size)
        return records_to_list(datas), count

    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    direction = request.raw_args.get('direction', 'up')
    datas, count = await mass_message_data(direction, current_page, page_size)
    page_info = get_page_info(page_size, current_page, count)
    return response_json(datas, page_info=page_info)


# @bp.route('/tasks/<task_id:[a-zA-Z0-9\\-]+>/message')
@protected()
@inject_user()
async def mass_message_detail_view(request, task_id, *args, **kwargs):
    '''群发消息详情'''
    async def mass_message_detail(id):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select group_ids::jsonb as "groups_info", content::jsonb, to_char(send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date 
                   from "group_task" where id=$1 and status<>3''')
            group_task = await st.fetchrow(id)
            if not group_task:
                return
            group_task = dict(group_task)
            gst = await con.prepare('select id, name from "group" where code = any($1) and status <> 3')
            group_codes = ujson.loads(group_task['groups_info'])
            groups = await gst.fetch(group_codes)
        group_task['groups_info'] = records_to_list(groups)
        group_task['content'] = ujson.loads(group_task['content'])
        return group_task
    data = await mass_message_detail(task_id)
    return response_json(data)


# @bp.route('/tasks/<task_id:[a-zA-Z0-9\\-]+>', methods=['DELETE'])
@protected()
@inject_user()
async def mass_message_detele_view(request, task_id, *args, **kwargs):
    '''群发消息撤回删除'''
    await redis.conn.zrem(TASK_MSG_MONITOR_REDIS_KEY, task_id)
    async with db.conn.acquire() as con:
        ut = await con.prepare('update "group_task" set status=3, update_date=now() where id=$1')
        await ut.fetchrow(task_id)
    return response_json(None)
