import os
import io
import xlsxwriter
from sanic.response import raw
from urllib.parse import quote

from app import db
from ut.response import response_json
from ut.utils import records_to_list, get_page_info

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with_draw_status = {
    0: ''' and "account_withdraw".review_status = 0 and "account_withdraw".status=0''',     # 待审核
    1: ''' and "account_withdraw".review_status = 1 and "account_withdraw".status=0''',     # 打款中
    2: ''' and "account_withdraw".review_status = 2 and "account_withdraw".status=2''',     # 未通过
    3: ''' and "account_withdraw".review_status = 1 and "account_withdraw".status=1''',     # 已打款
    4: ''' and "account_withdraw".review_status = 1 and "account_withdraw".status=2'''      # 打款失败
}


# @bp.route('/admin/withdraw', methods=['POST'])
async def withdraw_list_admin(request, *args, **kwargs):
    """提现列表"""
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    params = request.json

    sql, sql_count = await withdraw_sql(params)
    sql = sql + ''' limit ''' + str(page_size) + ''' offset ''' + str(current_page*page_size)

    async with db.conn.acquire() as con:
        select_result = records_to_list(await con.fetch(sql))
        select_count = await con.fetchval(sql_count)
    page_info = get_page_info(page_size, current_page, select_count)
    return response_json(select_result, page_info=page_info)


async def withdraw_sql(params):
    sort = params.get('sort', None)
    phone = params.get('phone', None)
    amount_begin = params.get('amount_begin', None)
    amount_end = params.get('amount_end', None)
    withdraw_date_begin = params.get('withdraw_date_begin', None)
    withdraw_date_end = params.get('withdraw_date_end', None)
    paid_date_begin = params.get('paid_date_begin', None)
    paid_date_end = params.get('paid_date_end', None)
    status = params.get('status', None)
    sql = '''select "account_withdraw".id::varchar , "user".phone, "account_withdraw".amount, 
             "account_withdraw".withdraw_resp ->> 'msg' as reason,
             to_char("account_withdraw".create_date, 'YYYY-MM-DD HH24:MI:SS') as create_date, 
             to_char("account_withdraw".paid_date, 'YYYY-MM-DD HH24:MI:SS') as paid_date, 
             case when "account_withdraw".review_status = 0 and "account_withdraw".status=0 then 0
                  when "account_withdraw".review_status = 1 and "account_withdraw".status=0 then 1
                  when "account_withdraw".review_status = 2 and "account_withdraw".status=2 then 2
                  when "account_withdraw".review_status = 1 and "account_withdraw".status=1 then 3
                  when "account_withdraw".review_status = 1 and "account_withdraw".status=2 then 4 
             end as status from "account_withdraw" left join "user" on "user".id = "account_withdraw".user_id 
             where "account_withdraw".status <> 3'''
    sql_count = '''select count(1) from "account_withdraw" left join "user" on "user".id = "account_withdraw".user_id 
                   where "account_withdraw".status <> 3'''
    if phone is not None and phone != "":
        phone = "'" + phone + "'"
        sql = sql + ''' and "user".phone = ''' + phone
        sql_count = sql_count + ''' and "user".phone = ''' + phone
    if amount_begin is not None and amount_begin != "":
        sql = sql + ''' and "account_withdraw".amount >=''' + str(amount_begin)
        sql_count = sql_count + ''' and "account_withdraw".amount >=''' + str(amount_begin)
    if amount_end is not None and amount_end != "":
        sql = sql + ''' and "account_withdraw".amount <=''' + str(amount_end)
        sql_count = sql_count + ''' and "account_withdraw".amount <=''' + str(amount_end)
    if withdraw_date_begin is not None:
        withdraw_date_begin = "'" + withdraw_date_begin + "'"
        withdraw_date_end = "'" + withdraw_date_end + "'"
        sql = sql + ''' and "account_withdraw".create_date >=''' + withdraw_date_begin \
              + ''' and "account_withdraw".create_date <= ''' + withdraw_date_end
        sql_count = sql_count + ''' and "account_withdraw".create_date >=''' + withdraw_date_begin \
                    + ''' and "account_withdraw".create_date <= ''' + withdraw_date_end
    if paid_date_begin is not None:
        paid_date_begin = "'" + paid_date_begin + "'"
        paid_date_end = "'" + paid_date_end + "'"
        sql = sql + ''' and "account_withdraw".paid_date >=''' + paid_date_begin \
              + ''' and "account_withdraw".paid_date <= ''' + paid_date_end
        sql_count = sql_count + ''' and "account_withdraw".paid_date >=''' + paid_date_begin \
                    + ''' and "account_withdraw".paid_date <= ''' + paid_date_end
    if status is not None and status != "":
        sql = sql + with_draw_status.get(int(status))
        sql_count = sql_count + with_draw_status.get(int(status))
    if sort is not None:
        sql = sql + ''' order by "account_withdraw".''' + sort['sort_key'] + ''' ''' + sort['value']
    return sql, sql_count


# @bp.route('/admin/withdraw/export', methods=['POST'])
async def export_result(request, *args, **kwargs):
    params = request.json
    sql, sql_count = await withdraw_sql(params)
    async with db.conn.acquire() as con:
        select_result = records_to_list(await con.fetch(sql))
    if not select_result:
        return response_json(None)
    title = ['phone', 'amount', 'create_date', 'paid_date', 'status']

    out = io.BytesIO()
    workbook = xlsxwriter.Workbook(out)
    worksheet = workbook.add_worksheet()
    for item in title:
        worksheet.write(0, title.index(item), item)
    for item in select_result:
        worksheet.write(select_result.index(item)+1, 0, item['phone'] if item['phone'] is not None else '')
        worksheet.write(select_result.index(item)+1, 1, item['amount'] if item['amount'] is not None else '')
        worksheet.write(select_result.index(item)+1, 2, item['create_date'] if item['create_date'] is not None else '')
        worksheet.write(select_result.index(item)+1, 3, item['paid_date'] if item['paid_date'] is not None else '')
        worksheet.write(select_result.index(item)+1, 4, item['status'] if item['status'] is not None else '')

    workbook.close()
    out.seek(0)
    filename = quote("提现列表.xlsx")
    return raw(out.getvalue(), headers={'Content-Disposition': 'attachment;filename*=utf-8{0}'.format(filename)},
               content_type='application/vnd.ms-excel;chartset=utf-8')


# @bp.route('/admin/problem/feedback', methods=['POST'])
async def problem_feedback(request, *args, **kwargs):
    current_page = int(request.raw_args.get('current_page', 0))
    page_size = int(request.raw_args.get('page_size', 20))
    params = request.json

    sql, sql_count = await problem_sql(params)
    sql = sql + ''' limit ''' + str(page_size) + ''' offset ''' + str(current_page*page_size)

    async with db.conn.acquire() as con:
        select_result = records_to_list(await con.fetch(sql))
        select_count = await con.fetchval(sql_count)

    for result in select_result:
        if result['code'] is not None:
            result['robot_info'] = result['name']+'('+result['wechat_no']+')'
    page_info = get_page_info(page_size, current_page, select_count)
    return response_json(select_result, page_info=page_info)


async def problem_sql(params):
    phone = params.get('phone', None)
    problem_id = params.get('problem_id', None)
    robot_code = params.get('robot_code', None)
    group_name = params.get('group_name', None)
    commit_date_begin = params.get('commit_date_begin', None)
    commit_date_end = params.get('commit_date_end', None)
    sql = '''select "user".phone, "user".nickname, "user_problem_category".title, "robot".code, "robot".name, 
             "robot".wechat_no, "user_problem".group_name, "user_problem".description, 
             to_char("user_problem".create_date, 'YYYY-MM-DD HH24:MI:SS') as create_date from "user_problem" left join 
             "user_problem_category" on "user_problem".problem_categoty_id = "user_problem_category".id left join "user" on 
             "user".id = "user_problem".user_id left join "robot" on "robot".id = "user_problem".robot_id where 
             "user_problem".status <>3'''
    sql_count = '''select count(1) from "user_problem" left join 
             "user_problem_category" on "user_problem".problem_categoty_id = "user_problem_category".id left join "user" on 
             "user".id = "user_problem".user_id left join "robot" on "robot".id = "user_problem".robot_id where 
             "user_problem".status <>3'''
    if phone is not None and phone != "":
        phone = "'" + phone + "'"
        sql = sql + ''' and "user".phone = '''+phone
        sql_count = sql_count + ''' and "user".phone = '''+phone
    if problem_id is not None and problem_id != "":
        problem_id = "'" + problem_id + "'"
        sql = sql + ''' and "user_problem_category".id = ''' + problem_id
        sql_count = sql_count + ''' and "user_problem_category".id = ''' + problem_id
    if robot_code is not None and robot_code != "":
        robot_code = "'" + robot_code + "'"
        sql = sql + ''' and "robot".code = ''' + robot_code
        sql_count = sql_count + ''' and "robot".code = ''' + robot_code
    if group_name is not None and group_name != "":
        group_name = "'" + group_name + "'"
        sql = sql + ''' and "user_problem".group_name = ''' + group_name
        sql_count = sql_count + ''' and "user_problem".group_name = ''' + group_name
    if commit_date_begin is not None and commit_date_begin != "":
        commit_date_begin = "'" + commit_date_begin + "'"
        commit_date_end = "'" + commit_date_end + "'"
        sql = sql + ''' and "user_problem".create_date >=''' + commit_date_begin \
              + ''' and "user_problem".create_date <= ''' + commit_date_end
        sql_count = sql_count + ''' and "user_problem".create_date >=''' + commit_date_begin \
                    + ''' and "user_problem".create_date <= ''' + commit_date_end

    sql = sql + ''' order by "user_problem".create_date desc'''
    return sql, sql_count


# @bp.route('/admin/problem/feedback/export', methods=['POST'])
async def problem_feedback_export(request, *args, **kwargs):
    params = request.json
    sql, sql_count = await problem_sql(params)
    async with db.conn.acquire() as con:
        select_result = records_to_list(await con.fetch(sql))
    if not select_result:
        return response_json(None)
    title = ['phone', 'nickname', 'title', 'code', 'robot_name', 'robot_wechat_no', 'group_name', 'description', 'create_date']
    out = io.BytesIO()
    workbook = xlsxwriter.Workbook(out)
    worksheet = workbook.add_worksheet()
    for item in title:
        worksheet.write(0, title.index(item), item)
    for item in select_result:
        worksheet.write(select_result.index(item)+1, 0, item['phone'] if item['phone'] is not None else '')
        worksheet.write(select_result.index(item)+1, 1, item['nickname'] if item['nickname'] is not None else '')
        worksheet.write(select_result.index(item)+1, 2, item['title'] if item['title'] is not None else '')
        worksheet.write(select_result.index(item)+1, 3, item['code'] if item['code'] is not None else '')
        worksheet.write(select_result.index(item)+1, 4, item['wechat_no'] if item['wechat_no'] is not None else '')
        worksheet.write(select_result.index(item)+1, 5, item['name'] if item['name'] is not None else '')
        worksheet.write(select_result.index(item)+1, 6, item['group_name'] if item['group_name'] is not None else '')
        worksheet.write(select_result.index(item)+1, 7, item['description'] if item['description'] is not None else '')
        worksheet.write(select_result.index(item)+1, 8, item['create_date'] if item['create_date'] is not None else '')

    workbook.close()
    out.seek(0)
    filename = quote("问题反馈列表.xlsx")
    return raw(out.getvalue(), headers={'Content-Disposition': 'attachment;filename*=utf-8{0}'.format(filename)},
               content_type='application/vnd.ms-excel;chartset=utf-8')


# @bp.route('/admin/problems')
async def get_problem_category(request, *args, **kwargs):
    """获取问题列表"""
    async with db.conn.acquire() as con:
        select_category = await con.prepare('''select id, title, seq_no, type from "user_problem_category" 
               where status !=3''')
        problem_category = records_to_list(await select_category.fetch())
        return response_json(problem_category)
