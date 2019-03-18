from __future__ import unicode_literals
import asyncio
import re
import ujson

from sanic.log import logger

from config import settings
from ut.constants import GROUP_USER_ROBOT_MAP_REDIS_KEY, KEYWORD_KEY_REDIS_KEY
from app import redis, db
from app.send_message import send_text_msg
from ut.utils import constant_data_cache

ALT_CONTENT = 'https://cloud.gemii.cc/lizcloud/fs/noauth/media/5c0e38c486c82a00170b4c4f'
ALT_URL = ''.join([settings['LOCALHOST'], '/grouppet/altme'])
ALT_USER_TITLE = '有人@你'
ALT_USER_DESC = '群里有人@你啦，请快去查看吧'
ALT_ROBOT_TITLE = '有人@小宠'
ALT_ROBOT_DESC = '群里有人@小宠啦，请快去查看吧'
DEFAULT_CONTENT = '小宠现在休息哦，请明天再来找小宠聊天吧~'
NO_CONTENT = '和我聊天需要加上具体内容哦~'

MATCH_ALT_USER = re.compile(r'(@[^s].*?[\\s| ])')


async def group_message_callback_view(data):
    '''
    过滤@关键字+@用户+@机器人的消息存库
    {
        "group_id": "20181111222222",
        "user_id": "20181111222222",
        "all": true,
        "at_users": ["20181111222222", "20181111222222"],
        "message_no": "20181111222222",
        "is_robot": true,
        "send_time": "1970-01-01 00:00:00",
        "type": 3,
        "content": "你好",
        "title": "",
        "desc": "",
        "url": "",
        "voice_time": ""
    }
    '''
    async def get_user_id(group_code):
        async with db.conn.acquire() as con:
            st = await con.prepare('select user_id from "group" where code=$1 and status <> 3')
            user_id = await st.fetchval(group_code)
        return user_id

    async def add_keyword_trigger_count(group_code, id):
        async with db.conn.acquire() as con:
            # TODO 考虑并发情况下事务问题
            user_id = await get_user_id(group_code)
            st = await con.prepare('''select keyword->$1 as keyword from "user" where id = $2''')
            result = dict(await st.fetchrow(id, user_id))
            keyword = ujson.loads(result['keyword'])
            keyword['trigger_times'] += 1
            insert_stmt = await con.prepare('''UPDATE "user" SET keyword = jsonb_set(keyword, $1, $2::jsonb),
             update_date = now() where id=$3 returning keyword -> $4 ->> $5''')
            real_trigger_times = await insert_stmt.fetchval({id}, ujson.dumps(keyword), user_id, id, 'trigger_times')
            logger.info(f'real trigger times: {real_trigger_times}')

    @constant_data_cache(GROUP_USER_ROBOT_MAP_REDIS_KEY, 'code')
    async def map_group_relationship(code):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select r.code as robot_code, u.code as user_code, g.id as group_id, g.code as group_code, g.user_id as user_id 
                   from "group" as g join "user" u on g.user_id=u.id join "robot_group_map" map on g.id=map.group_id
                   join "robot" r on r.id=map.robot_id where g.code=$1 and map.status<>3 and g.status<>3''')
            data = await st.fetchrow(code)
        if not data:
            return None
        return dict(data)

    async def match_keyword_temp(group_code, content, mem_code, data):
        group_trigger_data = await redis.conn.hget(KEYWORD_KEY_REDIS_KEY, group_code)
        keyword_tasks = []
        if group_trigger_data:
            keywords_data = ujson.loads(group_trigger_data)
            for k in keywords_data:
                if k['keyword'].strip() in content:
                    keyword_tasks.append(add_keyword_trigger_count(group_code, k['uuid']))
                    keyword_tasks.append(send_text_msg(data['robot_code'], mem_code, k['reply_content'], group_code))
            if keyword_tasks:
                await asyncio.gather(*keyword_tasks)
                return

    group_code = data.get('group_id')
    mem_code = data.get('user_id')
    content = data.get('content')
    at_users = data.get('at_users')
    if at_users:
        data = await map_group_relationship(code=group_code)
        if not data:
            logger.error(f'not match map relationship {group_code}')
            return
        if data['robot_code'] in at_users:
            asyncio.ensure_future(match_keyword_temp(group_code, content, mem_code, data))
