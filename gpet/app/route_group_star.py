import ujson
import datetime
import time
import asyncio

from sanic.log import logger
from sanic.response import json as resp_json

from app import db, redis
from app.route_launch import currency_launch_switch, LAUNCH_SWITCH_CLOSE
from app.route_shorten import long_to_short
from app.common import currency_delete_group
from app.send_message import send_text_msg, send_image_msg
from ut.constants import TIMING_NOTICE_STAR_REDIS_KEY, GroupCancelReason
from config import settings


# # 星级调整话术
# UPGRADE_STAR_FOUR_WORD = '恭喜主人，你的【{group_name}】星级被调整为4星了，收益增加到9元。\n邀请他人使用小宠赚钱，你也会有额外收益哦～'
# UPGRADE_STAR_FIVE_WORD = '恭喜主人，你的【{group_name}】星级被调整为5星了，收益增加到30元。\n邀请他人使用小宠赚钱，你也会有额外收益哦～'
# # 群星级未抓取到足够信息,暂定一星
# GROUP_STAR_NO_INFO_WORD = '主人，由于【{group_name}】太安静，暂定1星群。小宠会继续评估，如有提升会第一时间通知你哦～'
# 群星级初始评定1星
GROUP_STAR_INIT_ONE_WORD = '-------🎉报告主人🎉-------\n\n微信群：【{group_name}】\n舒适度：[Joyful]\n你获得了0.6元红包。不要灰心，小宠在群内投放的内容，群友阅读一次你就获得0.16元红包哦~\n\n👉查看舒适度说明：{star_url}'
# 群星级初始评定2星
GROUP_STAR_INIT_TWO_WORD = '-------🎉报告主人🎉-------\n\n微信群：【{group_name}】\n舒适度：[Joyful][Joyful]\n你获得了1.5元红包。拉小宠进更加活跃的群，红包更大哦。\n\n👉查看舒适度说明：{star_url}'
# 群星级初始评定3星
GROUP_STAR_INIT_THREE_WORD = '-------🎉报告主人🎉-------\n\n微信群：【{group_name}】\n舒适度：[Joyful][Joyful][Joyful]\n你获得了3元红包。拉小宠进其他微信群，可以获得更多红包哦。\n\n👉查看舒适度说明：{star_url}'
# 群星级初始评定4星
GROUP_STAR_INIT_FOUR_WORD = '-------🎉报告主人🎉-------\n\n微信群：【{group_name}】\n舒适度：[Joyful][Joyful][Joyful][Joyful]\n你获得了9元红包。邀请他人体验小宠，你也会有额外红包哦～\n\n👉查看舒适度说明：{star_url}'
# 群星级初始评定5星
GROUP_STAR_INIT_FIVE_WORD = '-------🎉报告主人🎉-------\n\n微信群：【{group_name}】\n舒适度：[Joyful][Joyful][Joyful][Joyful][Joyful]\n你获得了30元红包。邀请他人体验小宠，你也会有额外红包哦～\n\n👉查看舒适度说明：{star_url}'
# 群星级四星海报地址
GROUP_STAR_FOUR_POSTER_URL = '{host}/user/{user_id}/poster?type=fourstar'
# 群星级五星海报地址
GROUP_STAR_FIVE_POSTER_URL = '{host}/user/{user_id}/poster?type=fivestar'
# 群星级秘籍地址
GROUP_STAR_SKILL_URL = '{host}/grouppet/star?userId={user_id}'
# 元旦活动收益模板code
NEW_YEAR_GROUP_PROFIT_TEMPLATE_CODE = 'NEW_YEAR'
# 活动默认收益模板code
DEFAULT_GROUP_PROFIT_TEMPLATE_CODE = 'DEFAULT'
# 一星群数量限制
ONE_STAR_GROUP_COUNT_LIMIT = 20
# 一星群数量超过限制话术
ONE_STAR_MORE_THAN_LIMIT_WORD = '------- 报告主人 ------- \n\n微信群：【{group_name}】\n舒适度：[Joyful]\n舒适度太差，小宠不再入住，请把我拉到更舒适的群吧。'
# 一星群消息不足时提示话术
ONE_STAR_NO_MSG_WORD = '微信群【{group_name}】活跃度过低，舒适度过低，小宠先退下了，请主人将我拉入更活跃的群吧～'


# @bp.route('/groups/star', methods=['POST'])
async def group_star(request):
    """
    接收BI群星级评定
    {
        "command":"update_group_star",
        "data":[{
            "groupId":String,
            "state":number, //评星状态，0-undefined, 1-init 2-upgrade
            "star":number
        }]
    }
    """
    param = request.json
    logger.info(f'group start evaluate, req:{param}')
    command = param.get('command')
    data = param.get('data')
    if command != 'update_group_star':
        return resp_json({'resultCode': 100})
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(task_receive_group_star(data), loop)
    return resp_json({'resultCode': 100})


async def task_receive_group_star(data):
    for index in range(0, len(data), 200):
        results = []
        items = data[index: index + 200]
        for group_stars in items:
            results.append(receive_group_star(group_stars))
        await asyncio.gather(*results)
    logger.info(f'receive group star end')


async def receive_group_star(group_stars):
    group_code = group_stars.get('groupId')
    state = group_stars.get('state')
    star = group_stars.get('star')
    async with db.conn.acquire() as con:
        get_star_stmt = await con.prepare('''
            select "user".code as user_code, "user".id as user_id, "group".quality_level, "robot".code as robot_code, "group".name as group_name, "group".id as group_id from "group" 
            join "robot_group_map" on "group".id = "robot_group_map".group_id
            join "robot" on "robot_group_map".robot_id = "robot".id
            join "user" on "group".user_id = "user".id
            where "group".code = $1 and "group".status <> 3''')
        user_group = await get_star_stmt.fetchrow(group_code)
        if not user_group:
            return
        user_id = user_group.get('user_id')
        user_code = user_group.get('user_code')
        robot_code = user_group.get('robot_code')
        group_name = user_group.get('group_name')
        group_id = user_group.get('group_id')
    try:
        await update_group_star(star, group_code, user_code, user_id, robot_code, group_name, group_id, state)
    except Exception as e:
        logger.error(f'update group star error:{e}, group_code:{group_code}')


async def send_star_notice(user_id, user_code, robot_code, group_name, star, group_code, group_id, state):
    msg_content_url = None
    star_url = await long_to_short(GROUP_STAR_SKILL_URL.format(host=settings['LOCALHOST'], user_id=user_id))
    msg_content_new_year = None
    if star == 1:
        if await low_star_count_more_than_limit(user_id, star):
            await currency_delete_group(group_id, GroupCancelReason.STAR_LOW_LIMIT)
            msg_content = ONE_STAR_MORE_THAN_LIMIT_WORD.format(group_name=group_name)
        else:
            msg_content = GROUP_STAR_INIT_ONE_WORD.format(group_name=group_name, star_url=star_url)
        if state == 6:
            await currency_delete_group(group_id, GroupCancelReason.SESSION_LOW_LIMIT)
            msg_content = ONE_STAR_NO_MSG_WORD.format(group_name=group_name)
    elif star == 2:
        msg_content = GROUP_STAR_INIT_TWO_WORD.format(group_name=group_name, star_url=star_url)
    elif star == 3:
        msg_content = GROUP_STAR_INIT_THREE_WORD.format(group_name=group_name, star_url=star_url)
    elif star == 4:
        msg_content = GROUP_STAR_INIT_FOUR_WORD.format(group_name=group_name, star_url=star_url)
        # 发送四星海报
        msg_content_url = GROUP_STAR_FOUR_POSTER_URL.format(host=settings['LOCALHOST'], user_id=user_id)
        # 关闭投放开关
        await close_launch(group_code)
    elif star == 5:
        msg_content = GROUP_STAR_INIT_FIVE_WORD.format(group_name=group_name, star_url=star_url)
        # 发送五星海报
        msg_content_url = GROUP_STAR_FIVE_POSTER_URL.format(host=settings['LOCALHOST'], user_id=user_id)
        await close_launch(group_code)
    else:
        return
    if await in_sending_time():
        await send_text_msg(robot_code, user_code, msg_content)
        if msg_content_new_year is not None:
            await send_text_msg(robot_code, user_code, msg_content_new_year)
        if msg_content_url is not None:
            await send_image_msg(robot_code, user_code, msg_content_url)
    else:
        # 第二天八点发送
        await timing_send_msg(robot_code, user_code, msg_content, msg_content_url, msg_content_new_year)


async def update_group_star(star, group_code, user_code, user_id, robot_code, group_name, group_id, state):
    async with db.conn.acquire() as con:
        update_star_stmt = await con.prepare('''update "group" set quality_level = $1, update_date = now() where code = $2 and status <> 3''')
        await update_star_stmt.fetch(star, group_code)
    await save_group_star_record(star, group_code, state)
    await send_star_notice(user_id, user_code, robot_code, group_name, star, group_code, group_id, state)


async def in_sending_time():
    start_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'8:00:00', '%Y-%m-%d%H:%M:%S')
    end_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:59:59', '%Y-%m-%d%H:%M:%S')
    now = datetime.datetime.now()
    return start_time < now < end_time


async def timing_send_msg(robot_code, user_code, msg_content, msg_content_url, msg_content_new_year):
    msg_dict = {'robot_code': robot_code, 'user_code': user_code, 'msg_content': msg_content, 'msg_content_url': msg_content_url, 'msg_content_new_year': msg_content_new_year}
    await redis.conn.rpush(TIMING_NOTICE_STAR_REDIS_KEY, ujson.dumps(msg_dict))


async def save_group_star_record(star, group_code, state):
    now = time.localtime()
    update_date = time.strftime('%Y-%m-%d %H:%M:%S', now)
    group_star_record_dict = [{'update_date': update_date, 'star': star, 'state': state}]
    async with db.conn.acquire() as con:
        get_group_stmt = await con.prepare('''select quality_level_record from "group" where code = $1 and status <> 3 limit 1''')
        quality_level_record = await get_group_stmt.fetchval(group_code)
        if quality_level_record is not None:
            update_group_stmt = await con.prepare('''update "group" set quality_level_record = quality_level_record || $1, update_date = now() where code = $2 and status <> 3''')
        else:
            update_group_stmt = await con.prepare('''update "group" set quality_level_record = $1, update_date = now() where code = $2 and status <> 3''')
        await update_group_stmt.fetch(ujson.dumps(group_star_record_dict), group_code)


async def close_launch(group_code):
    groups = [{'rcv_task_flag': LAUNCH_SWITCH_CLOSE, 'code': group_code}]
    await currency_launch_switch(groups)


async def update_group_profit_template_to_default(group_code):
    async with db.conn.acquire() as con:
        get_group_profit_stmt = await con.prepare('''select id from "group_profit_template" where code = $1 and status <> 3''')
        default_profit_template_id = await get_group_profit_stmt.fetchval(DEFAULT_GROUP_PROFIT_TEMPLATE_CODE)
        update_group_stmt = await con.prepare('''update "group" set profit_template_id = $1 where code = $2 and status <> 3''')
        await update_group_stmt.fetch(default_profit_template_id, group_code)


async def low_star_count_more_than_limit(user_id, star):
    """判断此用户一星群数量是否大于20个"""
    async with db.conn.acquire() as con:
        low_star_group_count_stmt = await con.prepare('''select count(1) from "group" where status <> 3 and user_id = $1 and quality_level = $2''')
        group_count = await low_star_group_count_stmt.fetchval(user_id, star)
    if star == 1:
        return group_count > ONE_STAR_GROUP_COUNT_LIMIT
