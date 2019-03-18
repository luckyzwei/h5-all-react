'''
机器人方法调用
'''
import ujson
import ssl
import os

import aiohttp
from functools import wraps

from config import settings
from ut.base import csa


basic_path = os.path.abspath(os.path.dirname(__file__))

ROBOT_HOST = settings['ROBOT_HOST']
TRANSFERS_PAY = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
LAUNCH_HOST = settings['LAUNCH_HOST']
CAFILE_PATH = settings['CAFILE_PATH']
WXPAY_CLIENT_CERT_PATH = settings['WXPAY_CLIENT_CERT_PATH']
WXPAY_CLIENT_KEY_PATH = settings['WXPAY_CLIENT_KEY_PATH']


def _request(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        return await response.json()
    return wrapper


# ========== 通用请求方法 ============ #

async def do_get(url):
    '''通用get,返回格式非json'''
    return await csa.session.get(url)


@_request
async def do_get_json(url):
    '''通用get,返回格式json'''
    return await csa.session.get(url)


@_request
async def post_json(url, data):
    '''通用Post json'''
    return await csa.session.post(url, json=data)


# =========== 机器人服务请求 ========== #


@_request
async def group_message_request(data):
    '''群消息发送'''
    url = ROBOT_HOST + '/gbot/send_group_message'
    return await csa.session.post(url, json=data)


@_request
async def private_message_request(data):
    '''私聊消息发送'''
    url = ROBOT_HOST + '/gbot/send_private_message'
    return await csa.session.post(url, json=data)


@_request
async def group_mem_info(data):
    '''获取群成员信息'''
    url = ROBOT_HOST + '/gbot/users?user_ids=' + data
    return await csa.session.get(url)


@_request
async def update_robot_nickname(data):
    """修改机器人昵称"""
    url = ROBOT_HOST + '/gbot/modify_group_robot_nickname'
    return await csa.session.post(url, json=data)


@_request
async def activate_group(data):
    """开通群"""
    url = ROBOT_HOST + '/gbot/bind_group'
    return await csa.session.post(url, json=data)


@_request
async def sync_group_members(data):
    """发起同步群成员"""
    url = ROBOT_HOST + '/gbot/sync_group_members'
    return await csa.session.post(url, json=data)


@_request
async def get_group_info(group_code):
    url = ROBOT_HOST + '/gbot/group/{group_id}'
    url = url.format(group_id=group_code)
    return await csa.session.get(url)


@_request
async def cancel_group(data):
    '''注销群'''
    url = ROBOT_HOST + '/gbot/unbind_group'
    return await csa.session.post(url, json=data)


@_request
async def get_robot_quota(data):
    '''获取机器人开通的群列表'''
    url = ROBOT_HOST + '/gbot/robot/{robot_id}/groups'
    url = url.format(robot_id=data)
    return await csa.session.get(url)


@_request
async def get_robot_info(data):
    '''获取机器人基本信息'''
    url = ROBOT_HOST + '/gbot/robot/{robot_id}'
    url = url.format(robot_id=data)
    return await csa.session.get(url)


# ========== 外部对接服务 ========== #


async def wechate_transfers(data):
    '''微信企业向个人付款'''
    context = ssl.create_default_context(cafile=CAFILE_PATH)
    context.load_cert_chain(WXPAY_CLIENT_CERT_PATH, WXPAY_CLIENT_KEY_PATH)
    return await csa.session.post(url=TRANSFERS_PAY, data=data, ssl_context=context)


async def send_msg_montent(data):
    '''发送短信'''
    url = 'http://43.240.124.85:8901/sms/v2/std/single_send'
    return await csa.session.post(url, json=data)


@_request
async def req_launch_switch(data):
    '''群投放开关'''
    url = LAUNCH_HOST + '/launch-api/launch/syncslotinfo'
    return await csa.session.post(url, json=data)


@_request
async def send_customer_msg(data, url):
    '''发送客服消息'''
    return await csa.session.post(url, json=data)


@_request
async def upload_file_to_aliyun(data, url):
    '''上传文件到阿里云客服'''
    return await csa.session.post(url, data=data)


async def get_ai_response_msg(url, data):
    '''发送给ai数据'''
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(json_serialize=ujson.dumps, timeout=timeout) as session:
        return await session.post(url, json=data)


async def response_callback_launch(data):
    """投放结果反馈"""
    url = LAUNCH_HOST + '/launch-api/launch/updatelaunchresult'
    await csa.session.post(url, json=data)
