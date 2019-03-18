import decimal
import json
from uuid import UUID

from sanic.response import json as resp_json
from ut.constants import SERVICE_SUCCESS_CODE


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def _response(code=SERVICE_SUCCESS_CODE, msg='', data=None, page_info=None):
    rs = {
        'code': code,
        'description': msg,
        'data': None,
    }
    if data is not None:
        rs['data'] = data
    if page_info is not None:
        rs['page_info'] = page_info
    return rs


def response_json(data, code=SERVICE_SUCCESS_CODE, msg='', page_info=None, **kwargs):
    body = _response(code=code, msg=msg, data=data, page_info=page_info)
    return resp_json(body, dumps=json.dumps, cls=UUIDEncoder, **kwargs)


def dumps(data):
    return json.dumps(data, cls=UUIDEncoder)
