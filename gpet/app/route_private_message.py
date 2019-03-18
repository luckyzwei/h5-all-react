import asyncio
import ujson
import uuid

from sanic.log import logger

from app.common import get_robot_by_id, get_user_by_code, check_robot_amount_distribute, check_exists_master_group, \
    get_robot_by_code, active_user_operate
from config import settings
from ut.constants import MSGTYPE, MASS_MSG_TASK_CREATE_REDIS_KEY, MASS_MESSAGE_TRANC_REDIS_KEY, \
    CUSTOMER_MESSAGE_TRANC_REDIS_KEY
from app import redis
from ut.utils import aly_image_check
from app.route_shorten import long_to_short
from app.send_message import send_text_msg, send_image_msg, send_user_card_msg
from app.route_costomer_msg import send_msg_text_to_customer, send_msg_image_to_customer, apply_staff, user_offline

LOCALHOST = settings['LOCALHOST']

CHAT_MAP = {
    '菜单': '回复1，进入首页\n回复2，拉群方法\n回复3，生成海报邀请新用户\n回复4，常见问题及反馈\n回复5，进入客服模式\n回复6，查询小宠进群额度\n回复【菜单】，查看以上内容',
    '1': '点击 {short_url} 进入小宠物的首页',
    # '2': 'https://cloud.gemii.cc/lizcloud/fs/noauth/media/5c22e961a579e5001df6c5a4',
    '2': '拉群方法：{short_url}',
    '3': '保存你的专属二维码海报，邀请好友成为你的徒弟徒孙，他赚的多，你分的多。\n点击生成海报：{short_url}',
    '收徒': '保存你的专属二维码海报，邀请好友成为你的徒弟徒孙，他赚的多，你分的多。\n点击生成海报：{short_url}',
    '4': '{short_url}',
    '5': '您已进入客服排队系统，很高兴为您服务！我们将尽快为您安排服务顾问，请稍后......\n 如需退出客服模式，请回复【退出】。',
    '6': '我今天还可以开通群哦，快拉我进群吧',
    '7': '请先将需要群发的图片或链接或小程序先发给我哦，以我10分钟内先收到的第一个为准哦'
}
# 长链地址
# TODO [拉群gif图需更改]
HOME_PAGE_URL = ''.join([LOCALHOST, '/grouppet/home?userId={user_id}'])
SHARE_POSTER_URL = ''.join([LOCALHOST, '/user/{user_id}/poster'])
QUESTION_URL = ''.join([LOCALHOST, '/grouppet/question'])
PULL_GROUP_URL = ''.join([LOCALHOST, '/grouppet/import'])
CHECK_TASK_URL = ''.join([LOCALHOST, '/grouppet/createmess?task_id={task_id}'])

PULL_GROUP_IMAGE = 'https://cloud.gemii.cc/lizcloud/fs/noauth/media/5c22e961a579e5001df6c5a4'

# 客服
PET_USER_CARD = 'gh_aa91bd46d524'
CUSTOMER_MSG_MAP = {
    '509': '亲爱的主人，由于当前咨询量过大，暂时无法为您提供服务，您可以至小宠公众号“微小宠World”给我们留言',
    '508': '很抱歉，现在是非服务时间，请您在工作日9：30至18：30前来咨询。我们将竭诚为您服务!也可进入{short_url}查看常见问题及回答'
}
ENTER_CUSTOMER = ''
EXIST_CUSTOMER_MSG = '退出'
EXIST_CUSTOMER_REPLAY = '您已成功退出客服对话系统，感谢您对小宠的支持，欢迎您再次使用客服咨询系统。'
NOT_SUPPORT_MSG = '暂不支持当前类型的消息，请发送图片或文字消息与客服沟通'

# 群发消息
TIMOUT_MESSAGE = '由于您长时间未发送图片/链接/小程序，已退出群发消息。如需再次使用，可回复【6】'
ERROR_MESSAGE = '暂时不支持群发纯文本消息'
SENSITIVE_MESSAGE = '内容不符合安全标准'
STOP_MESSAGE = '已收到您的群发消息，请点击下面的链接去添加配套话术及选择群发的微信群和时间 {short_url} 如需更换图片/链接/小程序，请重新回复7开始操作'
NO_MASTER_GROUP_MSG = '群发消息属于群主功能，您还未导入群主群'
NO_AVAILABLE_AMOUNT_MSG = '您已超过当日群发消息创建最大次数，请明天再来创建群发任务'

# 机器人额度判定
OTHER_ROBOT_MSG = '我今天已经不能继续开通群啦，你可以找我的小伙伴继续开通'
NO_ROBOT_WORD = '主人，我今天体力消耗完了，现在也没有其他训练好的小宠物，请主人等到明天再拉我进群赚钱吧'

# 默认话术
DEFAULT_REPLY = '主人你是想我了吗[Shy]～ 回复【菜单】就能看到我提供的服务哦！'
USER_INFO_NOT_COMPLETE_MSG = '该功能需要先进入首页后方可使用，可回复1进入'

# 海报url
POSTER_URL = ''.join([LOCALHOST, '/grouppet/share'])

# 事务缓存
MASS_MESSAGE_TIMEOUT = 10 * 60
CUSTOMER_MESSAGE_TIMEOUT = 10 * 60
MASS_MSG_TASK_TIMEOUT = 10 * 60


class CONTENT:
    HOME_TYPE = '1'
    PULL_GROUP_TYPE = '2'
    POSTER_TYPE = '3'
    GET_SUB_USER = '收徒'
    QUESTION_TYPE = '4'
    CUSTOMER_TYPE = '5'
    ROBOT_AMOUNT = '6'
    MASS_MESSAGE_TYPE = '7'


async def private_message_callback_view(data):
    '''
    读取话术触发关键字与当前消息比对，满足则发送指定话术
    - 未匹配到任何关键字或者不在任何事务中时，发送默认话术
        - 群发消息事务
        - 客服消息事务
    - 进入某一事务中时，发送该事务中的话术
    - 匹配到关键字时，发送关键字话术
    {
        "robot_id": "20181111222222",
        "user_id": "20181111222222",
        "send_time": "1970-01-01T00:00:00",
        "type": 3,
        "content": "你好",
        "title": "",
        "desc": "",
        "url": "",
        "voice_time": ""
    }
    '''
    async def enter_mass_msg_trans(mem_code, robot_code):
        '''进入群发消息事务中'''
        mass_key = MASS_MESSAGE_TRANC_REDIS_KEY.format(mem_code=mem_code, robot_code=robot_code)
        await redis.conn.set(mass_key, mem_code, ex=MASS_MESSAGE_TIMEOUT)

    async def exit_mass_msg_trans(match_key):
        '''退出群发消息事务'''
        await redis.conn.delete(match_key)

    async def enter_customer_msg_trans(mem_code, robot_code, user_name):
        '''进入客服消息事务中'''
        customer_key = CUSTOMER_MESSAGE_TRANC_REDIS_KEY.format(mem_code=mem_code)
        value = ujson.dumps({'nickname': user_name, 'robot_code': robot_code})
        await redis.conn.set(customer_key, value, ex=CUSTOMER_MESSAGE_TIMEOUT)

    async def exit_customer_msg_trans(match_key):
        '''退出客服消息事务'''
        await redis.conn.delete(match_key)

    async def in_which_trans(mem_code, robot_code):
        mass_key = MASS_MESSAGE_TRANC_REDIS_KEY.format(mem_code=mem_code, robot_code=robot_code)
        match_mass_value = await redis.conn.get(mass_key)
        if not match_mass_value:
            customer_key = CUSTOMER_MESSAGE_TRANC_REDIS_KEY.format(mem_code=mem_code)
            customer_value = await redis.conn.get(customer_key)
            if not customer_value:
                return None, None
            return CONTENT.CUSTOMER_TYPE, customer_key
        return CONTENT.MASS_MESSAGE_TYPE, mass_key

    async def create_mass_msg_task(data):
        content = dict(data)
        content.pop('user_id')
        content.pop('robot_id')
        content.pop('send_time')
        task_id = str(uuid.uuid4())
        await redis.conn.set(MASS_MSG_TASK_CREATE_REDIS_KEY.format(task_id=task_id), ujson.dumps([content]), ex=MASS_MSG_TASK_TIMEOUT)
        logger.debug(f'mass msg task id: [{task_id}]')
        return task_id

    async def deal_mass_msg_trans(mem_code, robot_code, data, match_key):
        task_id = await create_mass_msg_task(data)
        await exit_mass_msg_trans(match_key)
        short_url = await long_to_short(CHECK_TASK_URL.format(task_id=task_id))
        await send_text_msg(robot_code, mem_code, STOP_MESSAGE.format(short_url=short_url))

    async def deal_customer_msg_trans(mem_code, robot_code, content, type, match_key):
        await redis.conn.expire(match_key, CUSTOMER_MESSAGE_TIMEOUT)
        if type == MSGTYPE.TEXT:
            await send_msg_text_to_customer(mem_code, robot_code, content)
        elif type == MSGTYPE.IMAGE:
            await send_msg_image_to_customer(mem_code, robot_code, content)
        else:
            await send_text_msg(robot_code, mem_code, NOT_SUPPORT_MSG)

    async def send_new_robot_distribute_msg(distribute_robot_id, robot_code, mem_code):
        robot = await get_robot_by_id(distribute_robot_id)
        await send_text_msg(robot_code, mem_code, OTHER_ROBOT_MSG)
        await asyncio.sleep(0.05)
        logger.debug(f'send robot {robot["id"]} qrcode {robot["qr_code"]}')
        await send_image_msg(robot_code, mem_code, robot['qr_code'])

    mem_code = data.get('user_id')
    robot_code = data.get('robot_id')
    msg_type = data.get('type')
    msg_content = data.get('content')
    pattern_type, match_key = await in_which_trans(mem_code, robot_code)
    user = await get_user_by_code(mem_code)
    if not user:
        logger.error(f'error mem code [{mem_code}], not match user id')
        return
    robot = await get_robot_by_code(robot_code)
    if not robot:
        logger.error(f'error robot code [{robot_code}], not match robot id')
        return
    user_id = user['id']
    await active_user_operate(user_id, 'chat_counts')
    if not pattern_type:
        if msg_type != MSGTYPE.TEXT:
            return
        content = msg_content.strip()
        if content not in CHAT_MAP.keys():
            await send_text_msg(robot_code, mem_code, DEFAULT_REPLY)
            return
        reply_content = CHAT_MAP[content]
        if content in [CONTENT.PULL_GROUP_TYPE, CONTENT.POSTER_TYPE, CONTENT.QUESTION_TYPE, CONTENT.MASS_MESSAGE_TYPE] \
            and not (user['open_id'] or user['union_id']):
            await send_text_msg(robot_code, mem_code, USER_INFO_NOT_COMPLETE_MSG)
            return
        if content == CONTENT.HOME_TYPE:           # 1
            home_short_url = await long_to_short(HOME_PAGE_URL.format(user_id=user_id))
            await send_text_msg(robot_code, mem_code, reply_content.format(short_url=home_short_url))

        elif content == CONTENT.PULL_GROUP_TYPE:   # 2
            pull_short_url = await long_to_short(PULL_GROUP_URL)
            await send_text_msg(robot_code, mem_code, reply_content.format(short_url=pull_short_url))
            await send_image_msg(robot_code, mem_code, PULL_GROUP_IMAGE)

        elif content == CONTENT.POSTER_TYPE or content == CONTENT.GET_SUB_USER:       # 3 or 收徒
            poster_url = SHARE_POSTER_URL.format(user_id=user_id)
            # await send_text_msg(robot_code, mem_code, reply_content)
            # await asyncio.sleep(0.05)
            # await send_image_msg(robot_code, mem_code, poster_url)
            poster_short_url = await long_to_short(POSTER_URL)
            await send_text_msg(robot_code, mem_code, reply_content.format(short_url=poster_short_url))
            await send_image_msg(robot_code, mem_code, poster_url)

        elif content == CONTENT.QUESTION_TYPE:     # 4
            question_short_url = await long_to_short(QUESTION_URL)
            await send_text_msg(robot_code, mem_code, reply_content.format(short_url=question_short_url))

        elif content == CONTENT.CUSTOMER_TYPE:     # 5
            apply_code = await apply_staff(mem_code, robot_code)
            if CUSTOMER_MSG_MAP.get(apply_code):
                if apply_code == '509':
                    await send_text_msg(robot_code, mem_code, CUSTOMER_MSG_MAP[apply_code])
                    await send_user_card_msg(robot_code, mem_code, content=PET_USER_CARD)
                elif apply_code == '508':
                    question_short_url = await long_to_short(QUESTION_URL)
                    await send_text_msg(robot_code, mem_code,
                                        CUSTOMER_MSG_MAP[apply_code].format(short_url=question_short_url))
            else:
                await enter_customer_msg_trans(mem_code, robot_code, user['nickname'])
                await send_text_msg(robot_code, mem_code, reply_content)

        elif content == CONTENT.ROBOT_AMOUNT:      # 6
            is_current_robot, distribute_robot_id = \
                await check_robot_amount_distribute(user_id, mem_code, user['channel'], robot_code)
            if is_current_robot:
                await send_text_msg(robot_code, mem_code, reply_content)
            elif not is_current_robot and distribute_robot_id:
                await send_new_robot_distribute_msg(distribute_robot_id, robot_code, mem_code)
            else:
                await send_text_msg(robot_code, mem_code, NO_ROBOT_WORD)
        elif content == CONTENT.MASS_MESSAGE_TYPE:  # 7
            if not await check_exists_master_group(mem_code):
                await send_text_msg(robot_code, mem_code, NO_MASTER_GROUP_MSG)
                return
            await enter_mass_msg_trans(mem_code, robot_code)
            await send_text_msg(robot_code, mem_code, reply_content)

        else:                                      # 菜单
            await send_text_msg(robot_code, mem_code, reply_content)
        return
    elif pattern_type == CONTENT.MASS_MESSAGE_TYPE:
        if msg_type not in [MSGTYPE.IMAGE, MSGTYPE.MINI_PROGRAM, MSGTYPE.LINK]:
            await send_text_msg(robot_code, mem_code, ERROR_MESSAGE)
            return
        if msg_type == MSGTYPE.IMAGE and not await aly_image_check(msg_content):
            await send_text_msg(robot_code, mem_code, SENSITIVE_MESSAGE)
            return
        await deal_mass_msg_trans(mem_code, robot_code, data, match_key)
        return
    elif pattern_type == CONTENT.CUSTOMER_TYPE:
        if msg_content.strip() == EXIST_CUSTOMER_MSG:
            await user_offline(mem_code, robot_code)
            await exit_customer_msg_trans(match_key)
            await send_text_msg(robot_code, mem_code, EXIST_CUSTOMER_REPLAY)
            return
        await deal_customer_msg_trans(mem_code, robot_code, msg_content, msg_type, match_key)
        return
    else:
        return
