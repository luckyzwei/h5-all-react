import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp

from sanic.response import stream
from app import db
from ut.response import response_json
from config import settings
from ut.constants import RESOURCE_NOT_FOUND_CODE
from sanic.log import logger
host = settings['LOCALHOST']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKGROUND_IMAGE = os.path.join(BASE_DIR, 'static/background.png')
QR_CODE_URL = host + '/grouppet/adopt'
GROUP_HOME_URL = ''.join([host, '/grouppet/home'])
FONT_PATH = os.path.join(BASE_DIR, 'ut/msyh.ttf')


# @bp.route('/user/<user_id:[a-zA-Z0-9\\-]+>/poster', methods=['GET'])
async def user_share_poster(request, user_id):
    """用户分享海报"""
    async def streaming_fn(response):
        await response.write(image_bytes.getvalue())
    type = request.raw_args.get('type', None)
    if type is not None:
        background_image = os.path.join(BASE_DIR, 'static/{}.png').format(type)
    else:
        background_image = os.path.join(BASE_DIR, 'static/background.png')
    user_info = await get_user_info(user_id)
    if user_info is None:
        return response_json({}, RESOURCE_NOT_FOUND_CODE, msg='用户不存在')
    head_url = user_info['head_url']
    name = user_info['nickname']
    channel = user_info.get('channel', None)
    qr_code_url = QR_CODE_URL + '?sharing_user_id=' + user_id
    if channel is not None:
        qr_code_url = qr_code_url + '&channel=' + channel
    image_bytes = await create_user_share_poster(qr_code_url, head_url, name, background_image, type)

    return stream(streaming_fn, content_type='image/jpeg')


# @bp.route('/gpet/poster', methods=['GET'])
async def init_poster(request):
    """初始海报"""
    async def streaming_fn(response):
        await response.write(image_bytes.getvalue())
    background_image = os.path.join(BASE_DIR, 'static/background.png')
    qr_code_url = QR_CODE_URL

    image_bytes = await create_user_share_poster(qr_code_url, None, None, background_image, None)
    return stream(streaming_fn, content_type='image/jpeg')


async def create_user_share_poster(qrcode_url, head_url, name, background_image, type):
    """
     创建群邀请海报
    :return:
    """
    if name == '' or name is None:
        name = '小宠'
    elif len(name) > 5:
        name = name[0:4] + '...'

    template_channel = 'star' if type is not None else 'default'
    template = await get_default_poster_model(template_channel)
    params = dict(url=qrcode_url, size=template['qrcode_size'], name=name, background_image=background_image,
                  x_offset=template['qrcode_xoffset'], y_offset=template['qrcode_yoffset'], head_url=head_url,
                  r=template['head_radius'], x_head=template['head_xoffset'], y_head=template['head_yoffset'],
                  font_size=template['font_size'], x_font=template['name_xoffset'], y_font=template['name_yoffset'])
    poster_img = await group_manage(**params)
    output_buffer = BytesIO()
    bg_image = poster_img.convert('RGB')
    bg_image.save(output_buffer, format='JPEG')
    return output_buffer


async def get_default_poster_model(template_channel):
    """
    获取默认海报模版
    """
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''select * from "poster_template" where status<>3 and channel=$1''')
        poster_template = await select_stmt.fetchrow(template_channel)

    return poster_template


async def get_user_info(user_id):
    """
    获取用户的头像，名字
    """
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare('''
                select nickname, head_url, channel from "user"
                where  id=$1
                ''')
        user_info = await select_stmt.fetchrow(user_id)

    return user_info


async def group_manage(**kwargs):
    """
    生成海报
    """
    qrcode_image = await create_qrcode_img(url=kwargs['url'], size=kwargs['size'])
    bg_image = await get_background_img(background_image=kwargs['background_image'])
    bg_image.paste(qrcode_image, (kwargs['x_offset'], kwargs['y_offset']), qrcode_image)

    if kwargs['head_url'] is not None and kwargs['head_url'] != '':
        try:
            head_image = await create_head_img(kwargs['head_url'], kwargs['r'])  # 切割圆形图像
            bg_image.paste(head_image, (kwargs['x_head'], kwargs['y_head']), head_image)
        except Exception as e:
            logger.info(f'head_url is invalidurl -> {e}')

    bg_image = await add_text_to_image(bg_image, kwargs['name'], kwargs['font_size'],
                                       kwargs['x_font'], kwargs['y_font'])

    return bg_image


async def create_qrcode_img(url, size):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image()
    image = image.convert('RGBA')
    image.thumbnail((size, size))
    return image


async def get_background_img(background_image):
    image = Image.open(background_image)
    image = image.convert('RGBA')
    return image


async def create_head_img(url, r):  # 生成圆形图片

    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        content = await response.read()
        image = Image.open(BytesIO(content))

        image = image.resize((2*r, 2*r), Image.ANTIALIAS)  # 缩放图片
        ima = image.convert('RGBA')
        size = image.size

        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            ima = ima.resize((r2, r2), Image.ANTIALIAS)
        r3 = r                                          # 圆形头像半径
        imb = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
        pima = ima.load()  # 像素的访问对象
        pimb = imb.load()
        r = float(r2 / 2)  # 圆心横坐标

    for i in range(r2):
        for j in range(r2):
            lx = abs(i - r)  # 到圆心距离的横坐标
            ly = abs(j - r)  # 到圆心距离的纵坐标
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径
            if l < r3:
                pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
    return imb


async def add_text_to_image(image, name, font_size, x_font, y_font):  # 加入文字
    # 将文字添加到图片
    font = ImageFont.truetype(FONT_PATH, font_size)            # 导入字体
    size = font.getsize(name)                                   # 文本宽度，高度

    text_overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)
    text_xy = ((x_font-size[0]/2), y_font)
    image_draw.text(text_xy, name, font=font, fill='#333333')
    image_with_text = Image.alpha_composite(image, text_overlay)
    return image_with_text


# @bp.route('/poster/background', methods=['POST'])
async def store_image_handler(request):
    test_file = request.files.get('test')
    if test_file is None:
        return response_json("no files for upload!")
    else:
        img = test_file.body
        with open(os.path.join(BASE_DIR, "./static/%s" % test_file.name), 'wb+') as f:
            f.write(img)

    return response_json('SUCCESS')
