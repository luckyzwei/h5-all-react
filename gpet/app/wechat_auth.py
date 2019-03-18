import ujson
import hashlib
import uuid
import time

from sanic.log import logger

from app import redis
from app.route_requests import post_json, do_get
from ut.constants import JS_API_TICKET_REDIS_KEY, WECHAT_AUTH_ERROR, GPET_WORLD_ACCESS_TOKEN_REDIS_KEY, OPEN_ACCESSTOKEN_REDIS_KEY
from ut.response import response_json


# 获取token url
GET_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={secret}&code={code}&grant_type=authorization_code'
# 开放平台app_id
OPEN_APP_ID = 'wx0333c84c2aa460ca'
# 开放平台secret
OPEN_APP_SECRET = '3da09c26e84e4ba02fac13ca24457711'
# 开放平台获取token url
OPEN_GET_ACCESSTOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
# 开放平台ticket
OPEN_TICKET = 'ticket@@@LGmh5PqS2A-wwIR4AvHhJEN_l7jwoloY5aj48hcxRo00Tihjap0fJeWA0UoqT_7xdQz9zn_m7VTq68BTbYRuAA'
# 获取用户信息url
WEB_GRANT_GET_USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={open_id}&lang=zh_CN'
# 微小宠world公众号app_id
GPET_WORLD_APP_ID = 'wx6f2f31d8d2b80e54'
# 微小宠world公众号secret
GPET_WORLD_APP_SECRET = '786af2d3f93d631f625845cd7eb0cbe2'
# 微小宠world公众号获取access_token url
GPET_WORLD_GET_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={secret}'
# 获取公众号分享ticket
GPET_TICKET_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi'
# 公众号分享ticket 签名
GPET_TICKET_SIGNATURE = 'jsapi_ticket={ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}'


# @bp.route('/wechat/user_info', methods=['GET'])
async def wechat_user_info(request):
    '''
    获取用户信息
    1. 通过code请求网页授权获取access_token以及open_id
    2. 根据access_token，open_id获取用户信息
    '''
    app_id = request.args.get("app_id")
    code = request.args.get("code")
    try:
        oauth_dict = await get_access_token(app_id, code)
        access_token = oauth_dict.get('access_token')
        open_id = oauth_dict.get('openid')
        user_info = await get_user_from_wechat(access_token, open_id)
        return response_json(user_info)
    except Exception:
        return response_json(None, WECHAT_AUTH_ERROR)


# @bp.route('/wechat/js/ticket', methods=['GET'])
async def js_api_ticket(request):
    '''获取微信分享ticket，主要用于页面分享'''
    app_id = request.args.get("app_id")
    url = request.args.get("url")
    redis_key = JS_API_TICKET_REDIS_KEY.format(app_id=app_id)
    # 根据app_id获取ticket
    if await redis.conn.exists(redis_key):
        ticket = await redis.conn.get(redis_key)
    else:
        ticket = await generate_ticket(app_id)
    # 签名用的随机字符串
    noncestr = str(uuid.uuid4())
    # 签名时间戳，精确到s
    timestamp = str(int(round(time.time())))
    signature = GPET_TICKET_SIGNATURE.format(ticket=ticket, noncestr=noncestr, timestamp=timestamp, url=url)
    hash_sha1 = hashlib.sha1()
    hash_sha1.update(signature.encode('utf-8'))
    signature = hash_sha1.hexdigest()
    resp_dict = {'app_id': app_id, 'timestamp': timestamp, 'noncestr': noncestr, 'signature': signature}
    return response_json(resp_dict)


async def generate_ticket(app_id):
    # 暂时没做app_id与secret对应关系，这里直接取secret
    redis_key = GPET_WORLD_ACCESS_TOKEN_REDIS_KEY.format(app_id=app_id)
    if await redis.conn.exists(redis_key):
        world_access_token = await redis.conn.get(redis_key)
    else:
        # 获取access_token
        get_token_url = GPET_WORLD_GET_ACCESS_TOKEN_URL.format(app_id=app_id, secret=GPET_WORLD_APP_SECRET)
        token_resp_json = await do_get(get_token_url)
        token_resp_json = ujson.loads(await token_resp_json.content.read(100000))
        logger.info(f'get access_token resp:{token_resp_json}')
        if 'errmsg' in token_resp_json:
            logger.info(f'获取token失败{token_resp_json}')
            raise Exception
        world_access_token = token_resp_json.get('access_token')
        expires_in = token_resp_json.get('expires_in')
        await redis.conn.set(redis_key, world_access_token, ex=expires_in - 200)
    get_ticket_url = GPET_TICKET_URL.format(access_token=world_access_token)
    ticket_resp_json = await do_get(get_ticket_url)
    ticket_resp_json = ujson.loads(await ticket_resp_json.content.read(100000))
    js_ticket = ticket_resp_json.get('ticket')
    expires_in = ticket_resp_json.get('expires_in')
    ticket_redis_key = JS_API_TICKET_REDIS_KEY.format(app_id=app_id)
    await redis.conn.set(ticket_redis_key, js_ticket, ex=expires_in - 200)
    return js_ticket


async def get_user_from_wechat(access_token, open_id):
    get_user_info_url = WEB_GRANT_GET_USER_INFO_URL.format(access_token=access_token, open_id=open_id)
    resp_json = await do_get(get_user_info_url)
    # 此处是为了把信息全部读出来
    resp_json = ujson.loads(await resp_json.content.read())
    if 'errmsg' in resp_json:
        logger.info(f'获取用户信息失败')
        raise Exception
    return resp_json


async def get_access_token(app_id, code):
    '''通过网页授权code获取access_token'''
    url = GET_ACCESS_TOKEN_URL.format(app_id=app_id, secret=GPET_WORLD_APP_SECRET, code=code)
    resp_json = await do_get(url)
    resp_json = ujson.loads(await resp_json.content.read())
    if 'errmsg' in resp_json:
        logger.info(f'获取token失败{resp_json}')
        raise Exception
    return resp_json


async def get_open_access_token():
    '''微信开放平台获取access_token'''
    if await redis.conn.exists(OPEN_ACCESSTOKEN_REDIS_KEY):
        return await redis.conn.get(OPEN_ACCESSTOKEN_REDIS_KEY)
    else:
        data = {'component_appid': OPEN_APP_ID, 'component_appsecret': OPEN_APP_SECRET, 'component_verify_ticket': OPEN_TICKET}
        access_token_resp = await post_json(OPEN_GET_ACCESSTOKEN_URL, data)
        access_token = access_token_resp.get('component_access_token')
        expires_in = access_token_resp.get('expires_in')
        await redis.conn.set(OPEN_ACCESSTOKEN_REDIS_KEY, access_token, ex=expires_in - 200)
