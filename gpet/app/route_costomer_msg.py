import time
import hmac
import uuid
import ujson
import os.path
import base64
import requests
from hashlib import sha1
from sanic.log import logger

from app import db, redis
from app.route_requests import send_customer_msg, do_get_json
from app.send_message import send_text_msg, send_image_msg
from ut.constants import CUSTOMER_SESSION_REDIS_KEY, CUSTOMER_SUCCESS_SESSION_REDIS_KEY
from ut.response import response_json


# 阿里云客服系统秘钥
ALIYUN_KEY = '56PIsKsVcfVytCciXeAPCGM0Qk6v5zC4'
# 获取客服成功
APP_STAFF_SUCCESS = '200'
# 获取客服成功不符合转人工
APP_STAFF_SUCCESS_ERROR = '516'
# 获取客服忙
APPLY_STAFF_BUSY = '509'
# 获取客服不在工作时间
APPLY_STAFF_NOT_WORKING = '508'
# 聊天窗编码
SCENE_ID = 'SCE00002499'
# 申请客服忙碌
CUSTOMER_BUSY_WORD = '由于当前咨询量过大，请稍后再试。'
# 接入客服忙碌
CUSTOMER_TOO_BUSY_WORD = '由于当前咨询量过大，小姐姐已经忙的飞起来了，请耐心等待，如需退出客服模式，请回复【退出】。'
# 阿里云客服上传文件Url
UPLOAD_FILE_URL = 'https://cschat-ccs.aliyun.com/openapi/uploadFile?tntInstId=_0v1ixma&src=outerservice&timestamp={timestamp}&digest={digest}'
# 阿里云客服发送消息Url
SEND_MSG_URL = 'https://cschat-ccs.aliyun.com/openapi/forwardMessage?tntInstId=_0v1ixma&scene={scene_id}&digest={digest}&timestamp={timestamp}&src=outerservice'
# 阿里云获取文件url
GET_FILE_URL = 'https://cschat-ccs.aliyun.com/openapi/fetchFile?tntInstId=_0v1ixma&src=outerservice&timestamp={timestamp}&digest={digest}&fileKey={file_key}'
# 退出客服系统话术
EXIT_CUSTOMER_WORD = '您已成功退出客服对话系统，感谢您对小宠的支持，欢迎您再次使用客服咨询系统。'
# 推送客服用户信息话术
USER_INFO_TO_CUSTOMER_WORD = '<系统消息>用户信息 \n 用户Id:-{user_id}\n昵称:{nickname}\n机器人code:{robot_code}'
# 文件类型list
IMAGE_TYPE_LIST = ['.PNG', '.JPEG', '.JPG', '.GIF']


# @bp.route('/aliyun/callback', methods=['POST'])
async def customer_msg_callback(request):
    '''接收阿里云回调消息(客服发送消息给用户)'''
    timestamp = request.raw_args.get('timestamp')
    digest = request.raw_args.get('digest')
    msg_json = request.json
    logger.info(f'receive aliyun callback msg, timestamp:{timestamp}, digest:{digest}, msg_json:{msg_json}')
    msg_type = msg_json.get('msgType')
    # 此处回调实际是user_code
    user_code = msg_json.get('userId')
    user_id = await get_user_id(user_code)
    # 队列缓存(可能在排队，实际未连接成功)
    queue_redis_key = CUSTOMER_SESSION_REDIS_KEY.format(user_code=user_code)
    # 客服连接成功缓存
    customer_success_redis_key = CUSTOMER_SUCCESS_SESSION_REDIS_KEY.format(user_code=user_code)
    if not await redis.conn.exists(queue_redis_key):
        return response_json(None)
    # 从redis中取回建立连接时缓存的user_info
    customer_info = ujson.loads(await redis.conn.get(queue_redis_key))
    nickname = customer_info.get('nickname')
    robot_code = customer_info.get('robot_code')
    if msg_type == 'event':
        event_type = msg_json.get('eventType')
        # 会话关闭
        if event_type == 'CONVERSATION_CLOSE':
            await redis.conn.delete(queue_redis_key)
            await redis.conn.delete(customer_success_redis_key)
            content = EXIT_CUSTOMER_WORD
            await send_text_msg(robot_code, user_code, content)
        # 超时
        elif event_type == 'VISITOR_OVERTIME_NOTICE':
            content = '<系统消息>' + msg_json.get('content')
            await send_msg_text_to_customer(user_code, None, content)
        # 建立会话
        elif event_type == 'CONVERSATION_CREATE':
            # 生成客服与用户session
            await redis.conn.set(customer_success_redis_key, None, ex=60 * 30)
            content = USER_INFO_TO_CUSTOMER_WORD.format(user_id=user_id, nickname=nickname, robot_code=robot_code)
            await send_msg_text_to_customer(user_code, None, content)
    else:
        msg_type = msg_json.get('msgType')
        content = msg_json.get('content')
        if msg_type == 'text':
            await send_text_msg(robot_code, user_code, content)
        elif msg_type == 'image':
            file_url = await get_file_url(content)
            await send_image_msg(robot_code, user_code, file_url)
    return response_json(None)


async def send_msg_text_to_customer(user_code, robot_code, content):
    '''发送文字消息到阿里云客服'''
    customer_success_redis_key = CUSTOMER_SUCCESS_SESSION_REDIS_KEY.format(user_code=user_code)
    # 客服未主动与用户建立session
    if not await redis.conn.exists(customer_success_redis_key):
        logger.info(f'user not connect success to customer, user_code:{user_code}')
        await send_text_msg(robot_code, user_code, CUSTOMER_TOO_BUSY_WORD)
        return None
    timestamp = int(round(time.time() * 1000))
    message = dict()
    message['userId'] = user_code
    message['msgType'] = 'text'
    message['content'] = content
    message['timestamp'] = timestamp
    res_code = await req_aliyun_send_msg(message, timestamp)
    await redis.conn.expire(customer_success_redis_key, 60 * 30)


async def send_msg_image_to_customer(user_code, robot_code, content):
    '''用户发送图片消息到阿里云客服'''
    customer_success_redis_key = CUSTOMER_SUCCESS_SESSION_REDIS_KEY.format(user_code=user_code)
    # 客服未主动与用户建立session
    if not await redis.conn.exists(customer_success_redis_key):
        logger.info(f'user not connect success to customer, user_code:{user_code}')
        await send_text_msg(robot_code, user_code, CUSTOMER_TOO_BUSY_WORD)
        return None
    timestamp = int(round(time.time() * 1000))
    res_json = await upload_file_to_customer(content, str(timestamp), user_code, robot_code)
    if res_json is not None:
        file_key = res_json.get('fileKey')
        if file_key is not None:
            message = dict()
            message['userId'] = user_code
            message['msgType'] = 'image'
            message['content'] = file_key
            message['timestamp'] = timestamp
            resp = await req_aliyun_send_msg(message, timestamp)
            logger.debug(f'aliyun sned msg resp:{resp}')
            await redis.conn.expire(customer_success_redis_key, 60 * 30)
    else:
        await send_msg_text_to_customer(user_code, robot_code, '<文件发送失败！>' + content)


async def upload_file_to_customer(file_url, timestamp, user_code, robot_code):
    file_ext = os.path.splitext(file_url)[1].upper()
    if file_ext not in IMAGE_TYPE_LIST:
        await send_msg_text_to_customer(user_code, robot_code, '<文件类型不支持！>' + file_url)
        return
    else:
        file_res = requests.get(file_url)
        file_base_64 = base64.b64encode(file_res.content)
        byte_array_file = bytearray(file_base_64)
        byte_array_timestamp = bytearray(timestamp.encode('utf-8'))
        byte_digest = byte_array_file + byte_array_timestamp
        file_name = str(uuid.uuid4()) + file_ext
        digest = hmac.new(ALIYUN_KEY.encode(), byte_digest, sha1).hexdigest()
        msg_url = UPLOAD_FILE_URL.format(timestamp=timestamp, digest=digest)
        data = {'type': 'image', 'base64File': file_base_64, 'fileName': file_name, 'timestamp': timestamp}
        resp = requests.post(msg_url, data=data)
        logger.debug(f'upload image to aliyun resp:{resp.json()}')
        return resp.json()


async def apply_staff(user_code, robot_code):
    '''请求分配客服'''
    logger.info(f'apply staff with user_code:{user_code}, robot_code:{robot_code}')
    timestamp = int(round(time.time() * 1000))  # 精确到ms
    message = dict()
    message['userId'] = user_code
    message['msgType'] = 'event'
    message['eventType'] = 'CONNECT_SERVER'
    message['skillGroupId'] = 100000000001
    message['timestamp'] = timestamp
    res_json = await req_aliyun_send_msg(message, timestamp)
    logger.debug(f'req aliyun resp:{res_json}')
    res_code = res_json.get('code')
    return res_code


async def req_aliyun_send_msg(message, timestamp):
    logger.info(f'req aliyun send msg:{message}, timestamp:{timestamp}')
    msg_json = ujson.dumps(message) + str(timestamp)
    digest = hmac.new(ALIYUN_KEY.encode(), msg_json.encode(), sha1).hexdigest()
    msg_url = SEND_MSG_URL.format(scene_id=SCENE_ID, digest=digest, timestamp=timestamp)
    logger.debug(f'request aliyun url:{msg_url}')
    resp = await send_customer_msg(message, msg_url)
    logger.debug(f'aliyun send msg resp:{resp}')
    return resp


async def get_user_id(user_code):
    async with db.conn.acquire() as con:
        get_user_id_stmt = await con.prepare('''select id from "user" where code = $1 and status <> 3 limit 1''')
        return await get_user_id_stmt.fetchval(user_code)


async def user_offline(user_code, robot_code):
    '''用户主动退出会话'''
    logger.info(f'user offline with user_id:{user_code}, robot_code:{robot_code}')
    timestamp = int(round(time.time() * 1000))  # 精确到ms
    message = dict()
    message['userId'] = user_code
    message['msgType'] = 'event'
    message['eventType'] = 'VISITOR_OFFLINE'
    message['timestamp'] = timestamp
    res_json = await req_aliyun_send_msg(message, timestamp)
    # 删除用户连接成功缓存
    customer_success_redis_key = CUSTOMER_SUCCESS_SESSION_REDIS_KEY.format(user_code=user_code)
    if await redis.conn.exists(customer_success_redis_key):
        await redis.conn.delete(customer_success_redis_key)
    return res_json.get('code')


async def get_file_url(file_key):
    timestamp = int(round(time.time() * 1000))  # 精确到ms
    key = file_key + str(timestamp)
    digest = hmac.new(ALIYUN_KEY.encode(), key.encode(), sha1).hexdigest()
    url = GET_FILE_URL.format(timestamp=timestamp, digest=digest, file_key=file_key)
    resp = await do_get_json(url)
    file_url = resp.get('url')
    logger.debug(f'download aliyun image url:{file_url}')
    return file_url
