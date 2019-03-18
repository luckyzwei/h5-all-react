import ujson
import asyncio
import base64
from itertools import groupby
from operator import itemgetter
import requests

from sanic.log import logger
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import inject_user

from app import db, redis
from app.route_requests import req_launch_switch, do_get, response_callback_launch
from app.send_message import send_text_msg, send_url_link_msg, send_image_msg, send_mini_program_msg
from ut.constants import TASK_SEND_RESULT_REDIS_KEY, NO_CLICK_GROUPS_REDIS_KEY
from ut.utils import records_to_value_list, records_to_list, get_page_info
from ut.response import response_json, dumps
from app.common import today

LAUNCH_SWITCH_CLOSE = 0   # 投放开关关
LAUNCH_SWITCH_OPEN = 1    # 投放开关开
LAUNCH_SOURCE = 2         # 群宠系统
LAUNCH_TYPE = 1           # 限制投放次数
LAUNCH_TIME_OPEN = -1     # 投放次数为-1表示不限制投放次数
LAUNCH_TIME_CLOSE = 0     # 投放次数为0表示不投放


# LAUNCH_TYPE = 2
# LAUNCH_SEND_STATUS_SUCCESS = 1
# LAUNCH_SEND_STATUS_FAIL = 2


# @bp.route('/launch/switch', methods=['PUT'])
@protected()
@inject_user()
async def launch_switch(request, *args, **kwargs):
    '''设置投放开关'''
    group_info = request.json
    await currency_launch_switch(group_info)
    return response_json(None, msg='设置成功')


# @bp.route('/launch/history')
@protected()
@inject_user()
async def launch_history(request, **kwargs):
    user_id = kwargs['user']['user_id']
    current_page = int(request.raw_args.get('current_page'))
    page_size = int(request.raw_args.get('page_size'))
    logger.debug(f'launch history req, user_id:{user_id}')
    async with db.conn.acquire() as con:
        user_task_stmt = await con.prepare(
            '''select id as task_id, to_char(send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date, jsonb_array_length(group_ids)::varchar as group_count, status as send_flag from "group_task"
                where user_id = $1 and type = 2 and status =1 and create_date >= (current_date  - 2)
                order by create_date desc limit $2 offset $3''')
        user_tasks = await user_task_stmt.fetch(user_id, page_size, current_page * page_size)
        task_list = records_to_list(user_tasks)
        history_count_stmt = await con.prepare(
            '''select count(1) from "group_task" where user_id = $1 and type = 2 and status = 1 and create_date >= (current_date - 2)''')
        total_records = await history_count_stmt.fetchval(user_id)
        page_info = get_page_info(page_size, current_page, total_records)
        return response_json(task_list, page_info=page_info)


# @bp.route('/launch/history/detail')
@protected()
@inject_user()
async def launch_history_detail(request, **kwargs):
    user_id = kwargs['user']['user_id']
    task_id = request.raw_args.get('task_id')
    logger.debug(f'get launch history detail, user_id:{user_id}, task_id:{task_id}')
    async with db.conn.acquire() as con:
        group_task_stmt = await con.prepare('''select group_ids, content, to_char(send_date, 'YYYY-MM-DD HH24:MI:SS') as send_date from "group_task" where id = $1''')
        group_task_res = await group_task_stmt.fetchrow(task_id)
        group_ids = ujson.loads(group_task_res.get('group_ids'))
        content = ujson.loads(group_task_res.get('content'))
        for task_item in content:
            if task_item.get('type') == 4:
                file_path = task_item.get('filePath')
                task_item.update({'filePath': file_path})
        send_date = group_task_res.get('send_date')
        get_group_stmt = await con.prepare('select name from "group" where id = any($1)')
        group_names = records_to_value_list(await get_group_stmt.fetch(group_ids), 'name')
        resp_dict = {'groups': group_names, 'materials': content, 'send_date': send_date}
    return response_json(resp_dict)


async def currency_launch_switch(group_info):
    if isinstance(group_info, list):
        launch_params = []
        for group in group_info:
            if group['rcv_task_flag'] == LAUNCH_SWITCH_CLOSE:
                data = {
                    'groupId': group['code'],
                    'limits': [{
                        'type': LAUNCH_TYPE,
                        'time': LAUNCH_TIME_CLOSE
                    }]
                }
                launch_params.append(data)
            elif group['rcv_task_flag'] == LAUNCH_SWITCH_OPEN:
                data = {
                    'groupId': group['code'],
                    'limits': [{
                        'type': LAUNCH_TYPE,
                        'time': LAUNCH_TIME_OPEN
                    }]
                }
                launch_params.append(data)

        request_params = {
            'command': 'update',
            'source': LAUNCH_SOURCE,
            'data': launch_params
        }
        logger.info(f'request launch switch params:{request_params}')
        try:
            resp = requests.post('http://ad.cloud.gemii.cc/launch-api/launch/syncslotinfo', json=request_params)
            resp_json = resp.json()
        except Exception as e:
            logger.error(f'request launch switch error:{e}')
            return
        logger.info(f'req_launch_switch,{resp_json}')
        if int(resp_json['resultCode']) == 100:
            async with db.conn.acquire() as con:
                for group in group_info:
                    update_group = await con.prepare('''update "group" set launch_switch = $1, update_date = now()
                                where code = $2 and status <> 3''')
                    await update_group.fetchrow(group['rcv_task_flag'], group['code'])


# @bp.route('/task/receive', methods=['POST'])
async def receive_task(request):
    """
    接收投放系统素材
    参数示例：
     {
        "taskId": string, //  任务id，用于追踪任务完成情况
        "taskType": number // 1-任务投放，2-会话
        "groupIds": ["string", "string"],
        "content": {
            "userCode": "",  //此字段适用于图灵@以及群内测试@
            "items": [
                {
                    "type": number // 内容类型，1-文字；2-图片；3-链接；4-小程序
                    "title": string // 标题，仅供链接、小程序使用，其他为空
                    "content": string // 内容，供文字、链接、小程序使用，其他为空(小程序为小程序的图片路径)
                    "filePath": string // 图片、视频、音频存放路径
                    "url": string // 链接为落地页，小程序为weburl
                }
            ]
        }
     }
    """
    try:
        task_req = request.json
        resource_id = str(task_req.get('taskId'))
        task_type = task_req.get('taskType')
        group_codes = task_req.get('groupIds')
        user_code = task_req.get('content').get('userCode')
        task_items = task_req.get('content').get('items')
        for task_item in task_items:
            item_type = task_item.get('type')
            if item_type == 4:
                item_file_path = task_item.get('filePath')
                xml_str = await mini_program_file_to_xml(item_file_path)
                task_item['filePath'] = xml_str
        if task_type == 1:
            logger.info(f'receive task params, resource_id:{resource_id}, group_codes_len:{len(group_codes)}, task_items:{task_items}')
        async with db.conn.acquire() as con:
            user_robot_group_stmt = await con.prepare('''
                select "group".user_id::varchar as user_id, "group".code as group_code, "group".id::varchar as group_id, robot.code as robot_code from "group" join robot_group_map on "group".id = "robot_group_map".group_id join robot on "robot_group_map".robot_id = "robot".id 
                where "group".code = any($1) and "group".status <> 3 order by "group".user_id ''')
            robot_groups = await user_robot_group_stmt.fetch(group_codes)
            logger.info(f'from db get data len:{len(robot_groups)}')
        user_groups = dict()
        for user_id, items in groupby(robot_groups, key=itemgetter('user_id')):
            items = list(items)
            user_groups.update({user_id: items})
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(task_send(resource_id, user_groups, task_items, user_code, task_type), loop)
        return response_json(None)
    except Exception as e:
        logger.error(f'receive task params error:{e}, resource_id:{resource_id}, group_codes_len:{len(group_codes)}, task_items:{task_items}')


async def task_send(resource_id, user_groups, task_items, user_code, task_type):
    if not user_groups:
        return
    user_ids = list(user_groups.keys())
    for index in range(0, len(user_ids), 1000):
        results = []
        items = user_ids[index: index+1000]
        for user_id in items:
            results.append(send_msg(resource_id, user_id, user_groups[user_id], task_items, user_code))
        await asyncio.gather(*results)
        await asyncio.sleep(0.3)
    logger.info('send msg end!')
    await save_task_res(resource_id, task_items, task_type)
    logger.info(f'task save end!')


async def send_msg(resource_id, user_id, user_groups, task_items, user_code):
    try:
        user_send_status = True
        send_status = True
        group_status = []
        for user_group in user_groups:
            group_id = user_group.get('group_id')
            group_code = user_group.get('group_code')
            robot_code = user_group.get('robot_code')
            for task_item in task_items:
                item_type = task_item.get('type')
                item_title = task_item.get('title')
                item_content = task_item.get('content')
                item_file_path = task_item.get('filePath')
                item_url = task_item.get('url')
                try:
                    if item_type == 1:  # 文字
                        if user_code:
                            resp = await send_text_msg(robot_code, [user_code], item_content, group_code)
                        else:
                            resp = await send_text_msg(robot_code, [], item_content, group_code)
                    elif item_type == 2:  # 图片
                        if user_code:
                            resp = await send_image_msg(robot_code, [user_code], item_file_path, group_code)
                        else:
                            resp = await send_image_msg(robot_code, [], item_file_path, group_code)
                    elif item_type == 3:  # 卡片链接
                        item_url = item_url.format(groupId=group_code)
                        if user_code:
                            resp = await send_url_link_msg(robot_code, [user_code], item_file_path, item_title, item_url, item_content, group_code)
                        else:
                            resp = await send_url_link_msg(robot_code, [], item_file_path, item_title, item_url, item_content, group_code)
                    elif item_type == 4:  # 小程序
                        if user_code:
                            resp = await send_mini_program_msg(robot_code, [user_code], item_file_path, item_title, item_content, '', group_code)
                        else:
                            resp = await send_mini_program_msg(robot_code, [], item_file_path, item_title, item_content, '', group_code)
                    else:
                        resp = {'code': '500'}
                except Exception as e:
                    logger.error(f'send msg to gbot error, {e}')
                    resp = {'code': '500'}
                # 保存任务及返回结果
                if int(resp.get('code')) != 100:
                    send_status = False
                    user_send_status = False
                    logger.error(f'send msg error:group_code:{group_code}, resp:{resp}')
                else:
                    send_status = True
            try:
                await callback_result(resource_id, group_code, send_status)
            except Exception as e:
                logger.error(f'callback group send status error, {e}')
            group_status.append({'group_id': group_id, 'status': send_status})
        redis_key = TASK_SEND_RESULT_REDIS_KEY.format(resource_id=resource_id)
        value_dict = {'groups': group_status, 'status': user_send_status}
        await redis.conn.hset(redis_key, user_id, dumps(value_dict))
    except Exception as e:
        logger.error(f'send task msg error {e}')


async def save_task_res(resource_id, task_items, task_type):
    redis_key = TASK_SEND_RESULT_REDIS_KEY.format(resource_id=resource_id)
    if task_type == 2:
        await redis.conn.delete(redis_key)
        return
    redis_dict = await redis.conn.hgetall(redis_key)
    rows = []
    for user_id, value in redis_dict.items():
        redis_val = ujson.loads(value)
        group_status = redis_val.get('groups')
        group_ids = [group['group_id'] for group in group_status]
        status = redis_val.get('status')
        # 保存的是只要有一个失败全部失败
        target_dict = (user_id, resource_id, ujson.dumps(group_ids), ujson.dumps(task_items), status)
        rows.append(target_dict)
    try:
        async with db.conn.acquire() as con:
            await con.executemany(
                '''insert into group_task (id, user_id, resource_id, group_ids, content, send_date, status, type)
                    values (uuid_generate_v4(), $1, $2, $3, $4, now(), $5, 2);''', rows)
    except Exception as e:
        logger.error(f'save group_task error:{e}')
    finally:
        await redis.conn.delete(redis_key)


async def mini_program_file_to_xml(file_path):
    # resp = await do_get(file_path)
    # return base64.b64decode(await resp.read()).decode('utf-8')
    resp = requests.get(file_path)
    return base64.b64decode(resp.content).decode('utf-8')


async def callback_result(resource_id, group_code, send_status):
    if send_status:
        state = 1
    else:
        state = 2
    param_dict = {'launchId': resource_id, 'groupId': group_code, 'state': state}
    logger.debug(f'callback result:{param_dict}')
    await response_callback_launch(param_dict)


async def no_click_groups(request):
    group_codes = request.json.get('group_codes')
    logger.info(f'receive BI no click groups, count:{len(group_codes)}')
    redis_key = NO_CLICK_GROUPS_REDIS_KEY.format(today=today())
    await redis.conn.set(redis_key, ujson.dumps(group_codes), ex=24*60*60)
    return response_json(None)
