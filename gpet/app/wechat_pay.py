import re
import hashlib
from random import Random
from sanic.log import logger

from app.route_requests import wechate_transfers
from ut.constants import TRANSFER_FAILED_CODE
from config import settings


'''公众平台支付的商户id'''
WX_PAY_MCH_ID = "1379133602"
'''公众平台支付的商户密钥'''


def format_url(params, api_key=None):
    """
    字典序排序
    :param params:
    :param api_key:
    :return:
    """
    url = "&".join(['%s=%s' % (key, params[key]) for key in sorted(params)])
    if api_key:
        url = '%s&key=%s' % (url, api_key)
    return url


def calculate_sign(params, api_key):
    """
    计算签名
    :param params:
    :param api_key:
    :return:
    """
    # 签名步骤一：按字典序排序参数, 在string后加入KEY
    url = format_url(params, api_key)
    # 签名步骤二：MD5加密, 所有字符转为大写
    return hashlib.md5(url.encode('utf-8')).hexdigest().upper()


def random_str():
    """
    生成32位随机字符串
    :return:
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    random = Random()
    return "".join([chars[random.randint(0, len(chars) - 1)] for i in range(32)])


def dict_to_xml(params):
    xml = ["<xml>", ]
    for k, v in params.items():
        xml.append('<%s>%s</%s>' % (k, v, k))
    xml.append('</xml>')
    return ''.join(xml)


def xml_to_dict(xml):
    xml = xml.strip()
    if xml[:5].upper() != "<XML>" and xml[-6:].upper() != "</XML>":
        return None, None

    result = {}
    sign = None
    content = ''.join(xml[5:-6].strip().split('\n'))

    pattern = re.compile(r"<(?P<key>.+)>(?P<value>.+)</(?P=key)>")
    m = pattern.match(content)
    while m:
        key = m.group("key").strip()
        value = m.group("value").strip()
        if value != "<![CDATA[]]>":
            pattern_inner = re.compile(r"<!\[CDATA\[(?P<inner_val>.+)\]\]>")
            inner_m = pattern_inner.match(value)
            if inner_m:
                value = inner_m.group("inner_val").strip()
            if key == "sign":
                sign = value
            else:
                result[key] = value

        next_index = m.end("value") + len(key) + 3
        if next_index >= len(content):
            break
        content = content[next_index:]
        m = pattern.match(content)

    return sign, result


async def weixin_transfers(amount, trade_no, desc, open_id, app_id):
    '''企业向个人转账'''
    amount = int(amount*100)     # 将元转换为分
    if not all([amount, trade_no, desc, open_id]) or amount < 100:
        return False, {'code': '400', 'msg': '参数错误', 'order': trade_no}

    wechat_params = {
        'mch_appid': app_id,                # 公众账号appid
        'openid': open_id,                  # 用户openid
        'partner_trade_no': trade_no,       # 商户订单号
        'amount': amount,                   # 转账金额单位分
        'desc': desc,                       # 企业付款描述信息
        'mchid': WX_PAY_MCH_ID,             # 商户号
        'nonce_str': random_str(),          # 随机字符串
        'check_name': 'NO_CHECK',           # 校验用户姓名选项 OPTION_CHECK
        'spbill_create_ip': '1.1.1.1',      # ip地址
    }
    params_sign = calculate_sign(wechat_params, settings['WX_PAY_KEY'])
    wechat_params['sign'] = params_sign
    xml = dict_to_xml(wechat_params)
    try:
        response = await wechate_transfers(xml)
        res_result = await response.content.read()
        result = xml_to_dict(res_result.decode('utf-8'))[1]
        if result is not None and result['result_code'] == 'SUCCESS':
            return True, {'code': '200', 'msg': 'success', 'order': trade_no}
        else:
            err_code = result['err_code']
            err_msg = result['err_code_des']
            logger.error(f'code [{TRANSFER_FAILED_CODE} msg transfer money failed! errcode: [{err_code}] errmsg: [{err_msg}]')
            return False, {'code': err_code, 'msg': err_msg, 'order': trade_no}
    except Exception as e:
        logger.error(f'transfer money occer error!!!, msg: {e}')
        return False, {'code': '500', 'msg': '微信接口调用失败', 'order': trade_no}
