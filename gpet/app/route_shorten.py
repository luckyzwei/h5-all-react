# -*- coding: utf-8 -*-
import re
from hashlib import md5
from urllib.parse import unquote, quote

from sanic import response

from app import redis
from config import settings
from ut.constants import SHORTEN_COUNTER_REDIS_KEY, SHORTEN_URL_REDIS_KEY, SHORTEN_CACHE_AWHILE
from ut.response import response_json
from ut.shorten_url import DEFAULT_ENCODER


TMP_SHORT_TIMEOUT = 10 * 60
SHORTEN_LOCALHOST = settings['LOCALHOST'] + '/s/'


# @bp.route('/s/<short:[a-zA-Z0-9\\-]+>')
async def redirect_to_long(request, short):
    short_url = ''.join([SHORTEN_LOCALHOST, short])
    long_url = await short_to_long(short_url)
    return response.redirect(long_url)


async def long_to_short_view(request):
    long_url = request.json.get('url')
    short_url = await long_to_short(long_url)
    return response_json(short_url)


async def get_shortens(long_num):
    '''批量生成短链'''
    shorten_num = await redis.conn.get(SHORTEN_COUNTER_REDIS_KEY)

    if shorten_num:
        shorten_num = int(shorten_num)
        await redis.conn.incrby(SHORTEN_COUNTER_REDIS_KEY, amount=long_num)
        start_num = shorten_num + 1
        end_num = shorten_num + long_num
    else:
        await redis.conn.incrby(SHORTEN_COUNTER_REDIS_KEY, long_num)
        start_num = 0
        end_num = long_num

    shortens = []
    for i in range(start_num, end_num+1):
        short_url = DEFAULT_ENCODER.encode_url(i)
        shortens.append(short_url)

    return shortens


def get_real_url(url):
    """给 URL 添加 scheme(qq.com -> http://qq.com)"""
    # 支持的 URL scheme
    # 常规 URL scheme
    scheme2 = re.compile(r'(?i)^[a-z][a-z0-9+.\-]*://')
    # 特殊 URL scheme
    scheme3 = ('git@', 'mailto:', 'javascript:', 'about:', 'opera:',
               'afp:', 'aim:', 'apt:', 'attachment:', 'bitcoin:',
               'callto:', 'cid:', 'data:', 'dav:', 'dns:', 'fax:', 'feed:',
               'gg:', 'go:', 'gtalk:', 'h323:', 'iax:', 'im:', 'itms:',
               'jar:', 'magnet:', 'maps:', 'message:', 'mid:', 'msnim:',
               'mvn:', 'news:', 'palm:', 'paparazzi:', 'platform:',
               'pres:', 'proxy:', 'psyc:', 'query:', 'session:', 'sip:',
               'sips:', 'skype:', 'sms:', 'spotify:', 'steam:', 'tel:',
               'things:', 'urn:', 'uuid:', 'view-source:', 'ws:', 'xfire:',
               'xmpp:', 'ymsgr:', 'doi:',
               )
    url_lower = url.lower()
    # 如果不包含规定的 URL scheme，则给网址添加 http:// 前缀
    scheme = scheme2.match(url_lower)
    if not scheme:
        for scheme in scheme3:
            url_splits = url_lower.split(scheme)
            if len(url_splits) > 1:
                break
        else:
            url = 'http://' + url
    return url


async def get_long_url(url):
    long_url = await redis.conn.hget(SHORTEN_URL_REDIS_KEY, url)
    return long_url


async def hset_short_url(set_info):
    '''批量保存'''
    await redis.conn.hmset(SHORTEN_URL_REDIS_KEY, set_info)


async def set_short_url(key, value):
    await redis.conn.hset(SHORTEN_URL_REDIS_KEY, key=key, value=value)


async def short_to_long(url):
    '''短链转换为长链'''
    if not url.startswith(SHORTEN_LOCALHOST):
        return None
    short_url = url.split(SHORTEN_LOCALHOST)[1]
    long_url = await get_long_url(short_url)
    return unquote(long_url) if long_url else None


async def long_to_short(url):
    '''生成单个短链'''
    url = quote(get_real_url(url))
    url_md5 = md5()
    url_md5.update(url.encode('utf-8'))
    url_md5 = url_md5.hexdigest()
    shorten = await redis.conn.get(SHORTEN_CACHE_AWHILE+url_md5)
    if not shorten:
        shortens = await get_shortens(1)
        shorten = shortens[0]
        await set_short_url(key=shorten, value=url)
        await redis.conn.set(SHORTEN_CACHE_AWHILE+url_md5, shorten, ex=TMP_SHORT_TIMEOUT)
    short_url = ''.join([SHORTEN_LOCALHOST, shorten])
    return short_url


async def long_to_shorts(urls):
    '''批量长链转短链'''
    if not isinstance(urls, list):
        raise TypeError('期待list类型参数`')
    shortens = await get_shortens(len(urls))
    absolute_short_urls = []
    set_info = {}
    for index_num, url in enumerate(urls):
        real_url = quote(get_real_url(url))
        short_url = shortens[index_num]
        set_info[short_url] = real_url
        absolute_url = ''.join([SHORTEN_LOCALHOST, short_url])
        absolute_short_urls.append(absolute_url)
    await hset_short_url(set_info)
    return absolute_short_urls
