import time
import ujson

from sanic.log import logger

from config import settings
from app.route_requests import get_ai_response_msg

APIURL = "http://openapi.tuling123.com/openapi/api/v2"
APIKEY = settings['TULING_APIKEY']
NO_CALL_COUNT_MSG = '小宠现在没有力气了，请一会儿再来找小宠聊天吧。'
LONG_CONTENT_MSG = '你的话太多了'
NO_IDENTIFICATION_MSG = '小宠没听懂你的意思呢，再跟我说一遍吧'


ERROR_MAP = {
    "5000": "无解析结果",
    "6000": "暂不支持该功能",
    "4000": "请求参数格式错误",
    "4001": "加密方式错误",
    "4002": "无功能权限",
    "4003": "该apikey没有可用请求次数",
    "4005": "无功能权限",
    "4007": "apikey不合法",
    "4100": "userid获取失败",
    "4200": "上传格式错误",
    "4300": "批量操作超过限制",
    "4400": "没有上传合法userid",
    "4500":  "userid申请个数超过限制",
    "4600": "输入内容为空",
    "4602": "输入文本内容超长(上限150)",
    "7002": "上传信息失败",
    "8008": "服务器错误",
       "0": "上传成功"
}


async def send_msg_to_ai(msg, user_id, group_id):
    '''

    :param msg: 消息内容
    :param user_id: 用户
    :param group_id: 群标识
    :return: [{
                "groupType": 1,
                "resultType": "",   // url、text、voice、video、image、news
                "values": {
                    "url\text\vioce\video\image\news": ""
                }
            }]
    '''
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": f"{msg}"
            }
        },
        "userInfo": {
            "apiKey": f"{APIKEY}",
            "userId": f"{group_id}"
        }
    }
    try:
        t = time.time()
        resp_data = await get_ai_response_msg(APIURL, data)
        logger.info(f'tuling call response time: {time.time() - t}')
        if not resp_data.content.is_eof():
            logger.debug('origin eof: %s' % resp_data.content.is_eof())
            resp_data.content.feed_eof()
        data = ujson.loads(await resp_data.text())
        intent = data.get('intent')
        if intent and intent.get('code'):
            if str(intent.get('code')) == '4602':
                return [{'values': {'text': LONG_CONTENT_MSG}}]
            elif str(intent.get('code')) in ['7002', '4600']:
                return [{'values': {'text': NO_IDENTIFICATION_MSG}}]
            elif ERROR_MAP.get(str(intent.get('code'))):
                logger.error(f"tuling group id: {group_id}, error code: {intent.get('code')}, msg: {ERROR_MAP.get(str(intent.get('code')))}")
                return [{'values': {'text': NO_CALL_COUNT_MSG}}]
            return data.get('results')
        else:
            logger.error(f'tuling response params error: {data}')
            return [{'values': {'text': NO_IDENTIFICATION_MSG}}]
    except Exception as e:
        logger.error(f'call tuling error: {e}')
        return [{'values': {'text': NO_IDENTIFICATION_MSG}}]


async def receive_ai_text_msgs(msg, user_id, group_id):
    '''接收到ai的文本消息'''
    datas = await send_msg_to_ai(msg, user_id, group_id)
    results = []
    if datas:
        for data in datas:
            text_msg = data.get('values').get('text')
            if text_msg:
                results.append(text_msg)
    if not results:
        results.append(NO_IDENTIFICATION_MSG)
    return results
