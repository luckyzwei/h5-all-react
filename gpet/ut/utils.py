import re
import asyncio
import functools
import inspect
import math
import time
import ujson
import random
import uuid
import datetime
import smtplib

from aredis import exceptions
from app import redis
from ut.response import dumps

from email.mime.text import MIMEText
from email.header import Header
from sanic.log import logger

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkgreen.request.v20180509 import TextScanRequest, ImageSyncScanRequest


EMAIL_RECEIVERS = ['wen.liu@gemii.cc']
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_USER = 'noreply@gemii.cc'
EMAIL_PASS = 'Jingege123'


def today():
    '''今日日期'''
    return datetime.datetime.now().strftime("%Y-%m-%d")


def yesterday():
    '''昨日天数'''
    yes_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    return yes_date.strftime("%Y-%m-%d")


def str_to_date(day):
    '''字符串转换为日期格式'''
    return datetime.datetime.strptime(day, '%Y-%m-%d')


async def acquire_lock(lockname, release_time=3, acquire_timeout=4):
    '''
    获取锁
    :param lockname: 锁名称
    :param acquire_timeout: 尝试获取锁时间
    :return: 获取锁失败返回False
    '''
    identifier = str(uuid.uuid4())
    lockname = 'lock:' + lockname
    lock_timeout = int(math.ceil(release_time))
    end = time.time() + acquire_timeout
    while time.time() < end:
        if await redis.conn.set(lockname, identifier, nx=True, ex=lock_timeout):
            return identifier
        await asyncio.sleep(0.05)
    return False


async def set_lock(lock_name, release_time=150):
    """
    获取锁
    :param lock_name: 锁名称
    :param release_time: 尝试获取锁时间
    :return: 获取锁失败返回False
    """
    identifier = str(uuid.uuid4())
    lock_name = 'lock:' + lock_name
    lock_timeout = int(math.ceil(release_time))
    if await redis.conn.set(lock_name, identifier, nx=True, ex=lock_timeout):
        return True
    return False


async def release_lock(lockname, identifier):
    '''
    释放锁
    :param lockname: 锁名称
    :param identifier: 获取锁时的值，用于释放锁
    :return:
    '''
    async with await redis.conn.pipeline() as pipe:
        lockname = 'lock:' + lockname
        while True:
            try:
                await pipe.watch(lockname)
                if await pipe.get(lockname) == identifier:
                    await pipe.delete(lockname)
                    await pipe.execute()
                    return True
                await pipe.unwatch()
                break
            except exceptions.WatchError:
                pass
        return False


def lock_function(lockname, lock_value, lock_timeout=2):
    '''
    方法中加锁的装饰器，未获取到锁的请求将被过滤调，慎用！！！
    :param lockname:
    :param lock_value:
    :param lock_timeout:
    :return:
    '''
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if await redis.conn.set(lockname, lock_value, nx=True, ex=lock_timeout):
                return await call(func, *args, **kwargs)
            return False
        return wrapper
    return decorator


def constant_data_cache(key, name, is_dumps=True):
    '''
     针对散列缓存读取与存储装饰
    :param key: 散列缓存的key
    :param name: 散列中对应的field
    :param is_dumps: 是否对value做序列化操作
    :return: str or list or dict
    '''
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name_key = kwargs.get(name)
            data = await redis.conn.hget(key, name_key)
            if data:
                if is_dumps:
                    return ujson.loads(data)
                else:
                    return data
            else:
                resp = await call(func, *args, **kwargs)
                if not resp:
                    return resp
                if is_dumps:
                    await redis.conn.hset(key, name_key, dumps(resp))
                else:
                    await redis.conn.hset(key, name_key, resp)
                return resp
        return wrapper
    return decorator


async def call(fn, *args, **kwargs):
    '''
    通用方法调用
    :param fn:
    :param args:
    :param kwargs:
    :return:
    '''
    if inspect.iscoroutinefunction(fn) or inspect.isawaitable(fn):
        fn = await fn(*args, **kwargs)
    elif callable(fn):
        fn = fn(*args, **kwargs)
    return fn


def get_random_num(start_num, end_num, reservations):
    '''获取随机数'''
    red_packed = random.uniform(start_num, end_num)
    r_red_packed = round(red_packed, reservations)
    return r_red_packed


def records_to_list(records):
    if records is None:
        return None
    result = []
    for record in records:
        result.append(dict(record))
    return result


def records_to_value_list(records, key):
    result = []
    for record in records:
        result.append(dict(record)[key])
    return result


def str_to_datetime(str):
    '''字符串转时间类型'''
    import datetime
    try:
        data = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        data = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return data


def get_page_info(page_size, current_page, total_records):
    '''获取分页信息'''
    if page_size == -1:
        total_page = 1
        page_size = total_records
    else:
        if total_records % page_size == 0:
            total_page = int(total_records/page_size)
        else:
            total_page = int(total_records/page_size)+1
    page_info = {
        'current_page': current_page,   # 当前第几页
        'page_size': page_size,         # 每页数量
        'total_page': total_page,       # 总页数
        'total_records': total_records  # 总数量
    }
    return page_info


def get_time():
    '''计算当前时间离当天23:59:59的相差秒数'''
    now = datetime.datetime.now()
    # 获取今天零点
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,microseconds=now.microsecond)
    # 获取23:59:59
    lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
    return (lastToday - now).seconds


def check_idcard(idcard):
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53":"云南", "54": "西藏", "61":"陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    idcard = str(idcard)
    idcard = idcard.strip()
    idcard_list = list(idcard)

    # 地区校验
    if not area[idcard[0:2]]:
        return 4
    # 15位身份号码检测
    if len(idcard) == 15:
        if (int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 ) :
            ereg = re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')      # 测试出生日期的合法性
        else:
            ereg = re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # 测试出生日期的合法性
        if re.match(ereg, idcard):
            return True
        else:
            return False
    # 18位身份号码检测
    elif len(idcard) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if (int(idcard[6:8])+1900) % 4 == 0 or ((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 ):
            ereg = re.compile('[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')   # 闰年出生日期的合法性正则表达式
        else:
            ereg = re.compile('[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')    # 平年出生日期的合法性正则表达式
        # 测试出生日期的合法性
        if re.match(ereg, idcard):
            # 计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]  # 判断校验位
            if M == idcard_list[17]:   # 检测ID的校验位
                return True
            else:
                return False
        else:
            return False
    else:
        return False


async def real_send_mail(mail_host, mail_user, mail_pass, sender, receivers, message):
    try:
        smtp = smtplib.SMTP()
        smtp.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(sender, receivers, message.as_string())
        logger.info(f'send email success')
        smtp.sendmail(sender, receivers, message.as_string())
        return True
    except Exception:
        logger.info(f'send email fail')
        return False


async def send_email(subject, content, receivers=None):
    logger.info(f'email send start, subject:{subject}, content:{content}')
    mail_host = EMAIL_HOST  # 设置服务器
    mail_user = EMAIL_USER  # 用户名
    mail_pass = EMAIL_PASS  # 口令
    sender = EMAIL_USER
    if receivers is None:
        receivers = EMAIL_RECEIVERS
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(mail_user, 'utf-8')
    message['To'] = Header(str(receivers), 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    return await real_send_mail(mail_host, mail_user, mail_pass, sender, receivers, message)


async def aly_text_check(content):
    if content is None or content == '':
        return True
    clt = AcsClient("LTAIMzATsuQaeFBH", "kplNM0IZ7MMO7Gg4dONZ8yWsBNOaTA", 'cn-shanghai')
    region_provider.modify_point('Green', 'cn-shanghai', 'green.cn-shanghai.aliyuncs.com')
    request = TextScanRequest.TextScanRequest()
    request.set_accept_format('JSON')
    task1 = {"dataId": str(uuid.uuid1()),
             "content": content,
             "time": datetime.datetime.now().microsecond
             }
    request.set_content(ujson.dumps({"tasks": [task1], "scenes": ["antispam"]}))
    response = clt.do_action_with_exception(request)
    result = ujson.loads(response)
    if 200 == result["code"]:
        task_results = result["data"]
        for task_result in task_results:
            if 200 == task_result["code"]:
                scene_results = task_result["results"]
                for sceneResult in scene_results:
                    label = sceneResult["label"]
                    if label != 'normal':
                        return False
                    return True
    return False


async def aly_image_check(image_url):
    clt = AcsClient("LTAIMzATsuQaeFBH", "kplNM0IZ7MMO7Gg4dONZ8yWsBNOaTA", 'cn-shanghai', 'cn-shanghai')
    region_provider.modify_point('Green', 'cn-shanghai', 'green.cn-shanghai.aliyuncs.com')
    request = ImageSyncScanRequest.ImageSyncScanRequest()
    request.set_accept_format('JSON')
    # 同步检测只支持对单张图片进行检测，即只有一个task
    task1 = {"dataId": str(uuid.uuid1()),
             "url": image_url,
             "time": datetime.datetime.now().microsecond
             }
    # 场景参数支持：porn（色情）、terrorism（暴恐）qrcode（二维码）、ad（图片广告）、ocr（文字识别）
    request.set_content(ujson.dumps({"tasks": [task1], "scenes": ["porn", 'terrorism', 'ad']}))
    response = clt.do_action_with_exception(request)
    result = ujson.loads(response)
    if 200 == result["code"]:
        task_results = result["data"]
        for task_result in task_results:
            if 200 == task_result["code"]:
                scene_results = task_result["results"]
                for scene_result in scene_results:
                    label = scene_result["label"]
                    if label != 'normal':
                        return False
                    return True
            else:
                return False
    else:
        return False
