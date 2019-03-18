import ujson

from aio_pika import IncomingMessage
from sanic.log import logger

from app.route_group_message import group_message_callback_view
from app.route_private_message import private_message_callback_view
from app.route_group import member_into_group_callback, member_retreat_group_callback,\
    robot_into_group_callback, group_activated_callback, group_sync, unbind_group
from app.route_user import member_info_call_back
from app.route_robot import robot_add_friend, robot_join_failed, robot_kicked, robot_blocked, robot_replace_success


GROUP_MSG_COMMAND = 'group_message'                # 群聊消息回调
PRIVATE_MSG_COMMAND = 'private_message'            # 私聊消息回调
GROUP_MEMBERS_COMMAND = 'group_members'            # 群成员信息回调
JOIN_GROUP_COMMAND = 'join_group'                  # 群用户入群回调
DROP_OUT_GROUP_COMMAND = 'drop_out_group'          # 群用户退群回调
ROBOT_ADD_FRIEND_COMMAND = 'robot_added'           # 机器人加（被加）好友回调
ROBOT_KICKED_COMMAND = 'robot_kicked'              # 机器人被踢回调
ROBOT_JOIN_GROUP_COMMAND = 'wait_for_bind'         # 待开通群回调（原机器人入群回调
OPEN_GROUP_SUCCESS_COMMAND = 'bind_group_success'  # 机器人开通群成功回调
ROBOT_BLOCKED_COMMAND = 'abnormal_robot'    # 机器人封号回调
ROBOT_REPLACE_SUCCESS_COMMAND = 'abnormal_robot_replaced'   # 机器人替换成功回调
GROUP_INFO_COMMAND = 'group_info'  # 群信息回调
ROBOT_JOIN_FAILED_COMMAND = 'robot_join_failed'  # 机器人入群失败回调
UNBIND_GROUP_SUCCESS = 'unbind_group_success'  # 注销群成功回调


async def on_message(message: IncomingMessage):
    with message.process():
        logger.debug(f'Receiver #: {message.body.decode("utf-8")}')
        data = ujson.loads(message.body.decode('utf-8'))
        command = data.get('command')
        body = data.get('body')
        if command == GROUP_MSG_COMMAND:
            await group_message_callback_view(body)


async def on_message_common(message: IncomingMessage):
    with message.process():
        data = ujson.loads(message.body.decode('utf-8'))
        command = data.get('command')
        body = data.get('body')
        if command == PRIVATE_MSG_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await private_message_callback_view(body)
        if command == JOIN_GROUP_COMMAND:
            await member_into_group_callback(body)
        if command == DROP_OUT_GROUP_COMMAND:
            await member_retreat_group_callback(body)
        if command == ROBOT_ADD_FRIEND_COMMAND:
            await robot_add_friend(body)
        if command == ROBOT_KICKED_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await robot_kicked(body)
        if command == ROBOT_JOIN_GROUP_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await robot_into_group_callback(body)
        if command == OPEN_GROUP_SUCCESS_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await group_activated_callback(body)
        if command == ROBOT_BLOCKED_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await robot_blocked(body)
        if command == ROBOT_REPLACE_SUCCESS_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await robot_replace_success(body)
        if command == ROBOT_JOIN_FAILED_COMMAND:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await robot_join_failed(body)
        if command == GROUP_INFO_COMMAND:
            await group_sync(body)
        if command == UNBIND_GROUP_SUCCESS:
            logger.info(f'Receiver #: {message.body.decode("utf-8")}')
            await unbind_group(body)


async def on_message_member(message: IncomingMessage):
    with message.process():
        data = ujson.loads(message.body.decode('utf-8'))
        command = data.get('command')
        body = data.get('body')
        logger.debug(f'Receiver #: {command}: {body[0]["group_id"]}: {len(body)}')
        if command == GROUP_MEMBERS_COMMAND:
            await member_info_call_back(body)
