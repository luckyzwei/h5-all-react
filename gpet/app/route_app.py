import ujson
from datetime import datetime

from sanic.log import logger

from app import redis
from app.common import active_user_operate
from ut.base import db, inner_mq
from ut.constants import POINT_WEB_QUEUE_NAME, USER_UNION_ID_MAP_REDIS_KEY
from ut.response import response_json
from ut.utils import constant_data_cache


# 系统状态 维护状态

APP_STATUS_REDIS_KEY = 'GPET:APP_STATUS'
APP_MARQUEE_REDIS_KEY = 'GPET:APP_MARQUEE'


# @bp.route('/app/status', methods=['GET'])
async def check_app_status(request):
    '''校验当前服务状态'''
    if await redis.conn.exists(APP_STATUS_REDIS_KEY):
        data = await redis.conn.get(APP_STATUS_REDIS_KEY)
        resp_json = ujson.loads(data)
        return response_json(resp_json)
    else:
        data = {'status': 1, 'upGradeEndTime': ''}
        return response_json(data)


# @bp.route('app/status', methods=['POST'])
async def set_app_status(request):
    '''设置app_status'''
    data = request.json
    data_json = ujson.dumps(data)
    await redis.conn.set(APP_STATUS_REDIS_KEY, data_json)
    return response_json(data)


async def generator_request_data(req, user_id=None):
    data = {"ip": req.remote_addr, "ua": req.headers.get('user-agent'),
            "dt": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
    data.update(req.raw_args)
    if user_id is not None:
        data.update({'_a1': user_id})
    return data


async def webpage_access_view(request):
    '''页面访问数据统计'''
    @constant_data_cache(USER_UNION_ID_MAP_REDIS_KEY, 'union_id', is_dumps=False)
    async def get_user_id_by_union_id(union_id):
        async with db.conn.acquire() as con:
            st = await con.prepare('select id::varchar from "user" where union_id=$1')
            user_id = await st.fetchval(union_id)
        return user_id

    union_id = request.raw_args.get('_a1')
    if not union_id:
        data = await generator_request_data(request)
        await inner_mq.send(POINT_WEB_QUEUE_NAME, {'command': 'page_access', 'body': data})
        return response_json(None)
    user_id = await get_user_id_by_union_id(union_id=union_id)
    if not user_id:
        logger.warning(f'{union_id} not find in user table')
        return response_json(None)
    data = await generator_request_data(request, user_id)
    await inner_mq.send(POINT_WEB_QUEUE_NAME, {'command': 'page_access', 'body': data})
    await active_user_operate(user_id, 'access_web_counts')
    return response_json(None)


async def set_marquee_info(request):
    """设置跑马灯"""
    date = request.json
    data_json = ujson.dumps(date)
    await redis.conn.set(APP_MARQUEE_REDIS_KEY, data_json)
    return response_json('SUCCESS')


async def get_marquee_info(request):
    """获取跑马灯状态"""
    if await redis.conn.exists(APP_MARQUEE_REDIS_KEY):
        marquee_content = await redis.conn.get(APP_MARQUEE_REDIS_KEY)
        resp_json = ujson.loads(marquee_content)
        return response_json(resp_json)
    else:
        data = {'status': 0, 'content': ''}
        return response_json(data)
