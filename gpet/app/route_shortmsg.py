import random
import re
import time
import hashlib
from urllib.parse import quote

from sanic.log import logger
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import inject_user

from app import redis
from ut.response import response_json
from app.route_requests import send_msg_montent
from ut.constants import SHORT_MSG_SEND_FREQUENTLY, SEND_MSG_VAL_REDIS_KEY, PARAMS_ERROR_CODE, SEND_MSG_RATE_REDIS_KEY, \
    SERVICE_SUCCESS_CODE, VERIFY_CODE_WRONG, VERIFY_CODE_EXPIRE


# 验证码模板
MSG_TEMPLATE = '您的验证码为{verify_code}，请于60分钟内填写。如非本人操作，请忽略本短信。'


# @bp.route('/sms/code/delivery', methods=['GET'])
@protected()
@inject_user()
async def send_verify_code(request, user):
    user_id = user.get('user_id')
    phone = request.args.get("phone", None)
    logger.info(f'user request verify_code, user_id:{user_id}, phone:{phone}')
    if phone is not None:
        check_phone_res = await check_phone(phone)
        if check_phone_res:
            '''
            发送验证码
            1. 正则校验手机号
            1. 根据手机号，生成6位随机数字
            2. 记录手机号与其验证码缓存关系
            '''
            if await check_rate(user_id, phone):
                return response_json(None, SHORT_MSG_SEND_FREQUENTLY, 'send frequently.')  # 调用频繁
            verify_code = str(random.randint(0, 999999)).zfill(6)
            val_redis_key = SEND_MSG_VAL_REDIS_KEY.format(user_id=user_id, phone=phone)
            await redis.conn.set(val_redis_key, verify_code, ex=60 * 60 * 1)
            content = MSG_TEMPLATE.format(verify_code=verify_code)
            return await send_msg(phone, content)
        else:
            return response_json(None, PARAMS_ERROR_CODE, 'this phone may not be exists.')
    else:
        return response_json(None, PARAMS_ERROR_CODE, 'this phone may not be exists.')


async def check_phone(phone):
    phone_pat = re.compile('^1[3-9]{1}\d{9}$')
    return re.search(phone_pat, phone)


# @bp.route('/sms/delivery/batch', methods=['POST'])
async def send_msg_batch(request):
    '''批量发送短信'''
    phones = request.json.get('phones')
    content = request.json.get('content')
    logger.info(f'batch send short_msg, phones:{phones}, content:{content}')
    for phone in phones:
        await send_msg(phone, content)
    return response_json(None)


async def send_msg(phone, content):
    timestamp = str(int(time.time()))
    user_id = 'JJ0679'
    pwd = '595489'
    m = hashlib.md5()
    pwd_str = user_id + '00000000' + pwd + timestamp
    m.update(bytes(pwd_str, encoding='utf-8'))
    pwd_md5 = m.hexdigest()
    params = {
        'userid': user_id,
        'pwd': pwd_md5,
        'mobile': phone,
        'content': quote(content.encode('gbk')),
        'timestamp': timestamp
    }
    await send_msg_montent(params)
    return response_json(None)


async def is_key_exists(key):
    '''缓存是否存在指定的key'''
    return await redis.conn.exists(key)


async def check_rate(user_id, phone):
    '''验证是否频繁发送'''
    rate_redis_key = SEND_MSG_RATE_REDIS_KEY.format(user_id=user_id)
    if await redis.conn.exists(rate_redis_key):
        # 频繁发送
        return True
    else:
        await redis.conn.set(rate_redis_key, None, ex=20)
        return False


async def verify_code_check(user_id, phone, verify_code):
    '''
    校验验证码
    '''
    logger.debug(f'user check verify_code is right,user_id:{user_id}, phone:{phone}, verify_code:{verify_code} ')
    redis_key = SEND_MSG_VAL_REDIS_KEY.format(user_id=user_id, phone=phone)
    if await redis.conn.exists(redis_key):
        redis_verify_code = await redis.conn.get(redis_key)
        if redis_verify_code == verify_code:
            await redis.conn.delete(redis_key)
            return SERVICE_SUCCESS_CODE
        else:
            return VERIFY_CODE_WRONG
    else:
        return VERIFY_CODE_EXPIRE
