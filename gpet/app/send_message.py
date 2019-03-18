'''
- 文本消息
- 图片消息
- 链接消息
- 小程序消息
'''
from sanic.log import logger

from ut.constants import MSGTYPE
from app.route_requests import group_message_request, private_message_request


BOT_MSG_SUCCESS = '100'


async def package_msg_data(type, **kwargs):
    data = dict(messages=[{'type': type, 'content': kwargs.pop('content'), 'title': kwargs.pop('title', ''),
                           'url': kwargs.pop('href', ''), 'desc': kwargs.pop('desc', ''), 'voice_time': '0',
                           'message_no': kwargs.pop('msg_no')}])
    if kwargs.get('group_id', None):
        user_id = kwargs.pop('user_id', [])
        if isinstance(user_id, list):
            data.update({'users': user_id, 'all': False})
        else:
            data.update({'users': [user_id], 'all': False})
        data.update(**kwargs)
        logger.debug(f'send group msg: {data}')
        resp = await group_message_request(data)
    else:
        kwargs.pop('group_id')
        data.update(**kwargs)
        logger.info(f'send private msg: {data}')
        resp = await private_message_request(data)
    if str(resp['code']) != BOT_MSG_SUCCESS:
        logger.warning(f'data: {data}, response: {resp}')
    return resp


async def send_text_msg(robot_code, member_code, content, group_code=None, msg_no=""):
    '''发送文本消息'''
    kw = {'robot_id': robot_code, 'user_id': member_code, 'content': content, 'group_id': group_code, 'msg_no': msg_no}
    return await package_msg_data(MSGTYPE.TEXT, **kw)


async def send_image_msg(robot_code, member_code, content, group_code=None, msg_no=""):
    '''发送图片消息'''
    kw = {'robot_id': robot_code, 'user_id': member_code, 'content': content, 'group_id': group_code, 'msg_no': msg_no}
    return await package_msg_data(MSGTYPE.IMAGE, **kw)


async def send_url_link_msg(robot_code, member_code, content, title, href, desc, group_code=None, msg_no=""):
    '''发送链接消息'''
    kw = {'robot_id': robot_code, 'user_id': member_code, 'content': content,
          'group_id': group_code, 'title': title, 'href': href, 'desc': desc, 'msg_no': msg_no}
    return await package_msg_data(MSGTYPE.LINK, **kw)


async def send_mini_program_msg(robot_code, member_code, content, title, href, desc, group_code=None, msg_no=""):
    '''发送消息'''
    kw = {'robot_id': robot_code, 'user_id': member_code, 'content': content,
          'group_id': group_code, 'title': title, 'href': href, 'desc': desc, 'msg_no': msg_no}
    return await package_msg_data(MSGTYPE.MINI_PROGRAM, **kw)


async def send_user_card_msg(robot_code, member_code, content, group_code=None, msg_no=""):
    '''发送消息'''
    kw = {'robot_id': robot_code, 'user_id': member_code, 'content': content, 'group_id': group_code, 'msg_no': msg_no}
    return await package_msg_data(MSGTYPE.USER_CARD, **kw)
