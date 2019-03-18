from decimal import Decimal
from itertools import groupby
from operator import itemgetter

from sanic.log import logger
from sanic_jwt.decorators import inject_user, protected

from app import db
from app.common import get_user_by_id, get_account_info
from config import settings
from ut.constants import RESOURCE_NOT_FOUND_CODE, PARAMS_ERROR_CODE, INSUFFICIENT_AMOUNT_CODE, \
    MISS_PHONE_CODE, MISS_IDCARD_CODE, REVOKED_TODAY_CODE, WITHDRAW_FAILED_CODE
from ut.response import response_json
from ut.utils import records_to_list


MD5_SECRET_KEY = settings['MD5_SECRET_KEY']

WITHDRAW_TAX_AMOUNT = 800   # 达到收税标准值
INCOME_TYPE = 1             # 收入
PAYMENT_TYPE = 2            # 支出
WITHDRAWING = 0             # 提现中
WITHDRAW_SUCCESSED = 1      # 提现成功
WITHDRAW_REJECTED = 2       # 拒绝提现
REVIEWING = 0               # 审核中
WITHDRAW_AGREE = 1          # 审核通过
REVIEW_REJECTED = 2         # 审核失败


BALABCE_DETAIL = {
    0: {'slip_type': 0, 'balance': '0'},
    1: {'slip_type': 1, 'balance': '0'},
    2: {'slip_type': 2, 'balance': '0'},
    3: {'slip_type': 3, 'balance': '0'},
    4: {'slip_type': 4, 'balance': '0'}
}


async def find_account_info(user_id):
    async with db.conn.acquire() as con:
        account_stmt = await con.prepare('select id, balance_amount from "account" where user_id=$1')
        account = await account_stmt.fetchrow(user_id)
    return account


# @bp.route('/profit')
@protected()
@inject_user()
async def user_incomes_view(request, user):
    '''用户收益'''
    user_id = user.get('user_id')
    account = await find_account_info(user_id)
    if not account:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='未找到对应的账户信息')
    account_id = account['id']
    async with db.conn.acquire() as con:
        # 总收益
        balance_stmt = await con.prepare(
            '''select cumulative_income from account where id=$1''')
        # 昨日收益
        yesterday_stmt = await con.prepare(
            '''select case when sum(case when balance_type = 1 then change_amount when balance_type = 2 then -change_amount end) 
               is not null then sum(case when balance_type = 1 then change_amount when balance_type = 2 then -change_amount end)
               else '0.00' end as balance from "account_slip" 
               where account_id=$1 and amount_type<>9 and settle_date = timestamp 'yesterday'::date''')
        total_balance = await balance_stmt.fetchval(account_id)
        yesterday_balance = await yesterday_stmt.fetchval(account_id)
    results = {'summary': {'amount': account['balance_amount'], 'balance': total_balance, 'yesterday_balance': yesterday_balance}}
    return response_json(results)


# @bp.route('/profit/slip')
@protected()
@inject_user()
async def user_incomes_detail_view(request, user):
    '''指定日期收益明细'''
    async def account_stat(account_id):
        async with db.conn.acquire() as con:
            balance_detail = await con.prepare(
                '''select to_char(settle_date, 'YYYY-MM-DD') as day, 
                   sum(case when balance_type = 1 then change_amount else -change_amount end) as balance_detail 
                   from "account_slip" where account_id=$1 and create_date::date >= (current_date - interval '14' day) 
                   and amount_type <> 9 group by day order by day desc''')
            balance = await balance_detail.fetch(account_id)
        return records_to_list(balance)

    async def day_account_detail(account_id):
        async with db.conn.acquire() as con:
            select_stmt = await con.prepare(
                '''select sum(case when balance_type = 1 then change_amount when balance_type = 2 then -change_amount end)::varchar as balance,
                   case when amount_type = 1 then 0 when amount_type =2 then 1 when amount_type in (3, 4) then 2 
                   when amount_type = 8 then 3 when amount_type in (5, 10) then 4 end as slip_type,
                   to_char(settle_date, 'YYYY-MM-DD') as day from "account_slip" 
                   where account_id=$1 and create_date >= current_date - interval '14' day
                   and amount_type not in (6, 7, 9)  group by day, slip_type order by day desc, slip_type''')
            day_balance_detail = await select_stmt.fetch(account_id)
        return records_to_list(day_balance_detail)

    user_id = user.get('user_id')
    account = await find_account_info(user_id)
    if not account:
        return response_json(None, code=RESOURCE_NOT_FOUND_CODE, msg='未找到对应的账户信息')
    account_stastics = await account_stat(account['id'])
    results = []
    for day, items in groupby(await day_account_detail(account['id']), key=itemgetter('day')):
        for stat_day in account_stastics:
            if stat_day['day'] == day:
                copy_detail = dict(BALABCE_DETAIL)
                copy_items = list(items)
                for item in copy_items:
                    item.pop('day')
                    copy_detail.pop(item['slip_type'])
                copy_items.extend(list(copy_detail.values()))
                copy_items.sort(key=lambda x: x['slip_type'])
                stat_day.update({'detail': copy_items})
                results.append(stat_day)
                break
    return response_json(results)


# @bp.route('/withdraw')
@protected()
@inject_user()
async def user_withdraw_view(request, user):
    '''用户提现页'''
    user_id = user.get('user_id')
    data = {}
    async with db.conn.acquire() as con:
        select_stmt = await con.prepare(
            '''select id, user_id, balance_amount, withdrawing_amount from "account" where user_id=$1''')
        user_withdraw_info = dict(await select_stmt.fetchrow(user_id))
        slip_stmt = await con.prepare(
            '''select exists(select id from "account_withdraw" where account_id=$1 and status in ($2, $3) limit 1)''')
        is_withdrawed = await slip_stmt.fetchval(user_withdraw_info['id'], WITHDRAW_SUCCESSED, WITHDRAWING)
    data.update({'is_withdrawed': is_withdrawed})
    data.update(user_withdraw_info)
    return response_json(data)


# @bp.route('/withdraw', methods=['POST'])
@protected()
@inject_user()
async def user_withdraw_request_view(request, user, *args, **kwargs):
    '''用户发起提现请求'''
    async def static_user_withdrow_balance_month(account_id):
        async with db.conn.acquire() as con:
            select_stmt = await con.prepare(
                '''select case when sum(amount) is not null then sum(amount) else 0 end as balance from "account_withdraw" 
                   where account_id=$1 and status=any($2) and create_date >= date_trunc('month', current_date)''')
            balance = await select_stmt.fetchval(account_id, [WITHDRAWING, WITHDRAW_SUCCESSED])
        return balance

    async def add_user_withdraw_record(account_id, user_id, amount):
        async with db.conn.acquire() as con:
            async with con.transaction():
                insert_stmt = await con.prepare(
                    '''insert into "account_withdraw" (id, account_id, user_id, amount, review_status, status)
                       values(uuid_generate_v4(), $1, $2, $3, 0, 0)
                    ''')
                update_stmt = await con.prepare(
                    '''update "account" set balance_amount = balance_amount-$1, 
                       withdrawing_amount = withdrawing_amount+$2, update_date=now() where id=$3''')
                await insert_stmt.fetch(account_id, user_id, amount)
                await update_stmt.fetch(amount, amount, account_id)

    async def is_withdraw_today(account_id):
        async with db.conn.acquire() as con:
            st = await con.prepare(
                '''select exists(select id from "account_withdraw" where account_id=$1 
                   and status=$2 and create_date >= timestamp 'today')''')
            is_withdraw = await st.fetchval(account_id, WITHDRAWING)
        return is_withdraw

    user_id = user.get('user_id')
    withdraw_balance = request.json.get('balance', None)
    balance_amounts = [1, 20, 50, 100, 200, 500]
    # 余额参数校验
    if withdraw_balance is None or withdraw_balance not in balance_amounts:
        return response_json(None, code=PARAMS_ERROR_CODE, msg='未获取到提现金额参数')
    account_info = dict(await get_account_info(user_id))
    if account_info['balance_amount'] < withdraw_balance:
        return response_json(None, code=INSUFFICIENT_AMOUNT_CODE, msg='提现金额超过当前余额')
    # 用户校验
    user_info = dict(await get_user_by_id(user_id))
    if not user_info.get('phone'):
        return response_json(None, code=MISS_PHONE_CODE, msg='请补全用户手机号')
    if user_info.get('status', 1) == 2:
        return response_json(None, code=WITHDRAW_FAILED_CODE, msg='用户已封号禁止提现')
    month_withdraw_balance = await static_user_withdrow_balance_month(account_info['id'])
    # 超800税收身份证信息补全提醒
    if month_withdraw_balance + Decimal(withdraw_balance) > WITHDRAW_TAX_AMOUNT:
        if not user_info.get('identity_info'):
            return response_json(None, code=MISS_IDCARD_CODE, msg='请补全用户身份证信息')
    if await is_withdraw_today(account_info['id']):
        return response_json(None, code=REVOKED_TODAY_CODE, msg='今天已提现')
    logger.info(f'user [{user_id} request withdraw balance [{withdraw_balance}]')
    await add_user_withdraw_record(account_info['id'], user_id, withdraw_balance)
    return response_json(None, msg='提现进入审核状态')


# @bp.route('/withdraw/review', methods=['POST'])
async def change_withdraw_record(request, *args, **kwargs):
    async def withdraw_record(id):
        async with db.conn.acquire() as con:
            st = await con.prepare('select id, account_id, amount from "account_withdraw" where id=$1')
            data = await st.fetchrow(id)
        return data

    withdraw_infos = request.json.get('withdraw_id')
    status = request.json.get('status')
    if isinstance(withdraw_infos, list):
        for withdraw in withdraw_infos:
            wd = await withdraw_record(withdraw)
            if not wd:
                return response_json(None, code=PARAMS_ERROR_CODE)
            if status == WITHDRAW_REJECTED:
                await withdraw_rejected_account(wd['account_id'], wd['id'], wd['amount'])
            elif status == WITHDRAW_AGREE:
                await withdraw_agree_account(wd['id'])
    else:
        return response_json(None, code=PARAMS_ERROR_CODE)
    return response_json(None)


async def withdraw_rejected_account(account_id, withdraw_id, amount):
    '''拒绝提现'''
    async with db.conn.acquire() as con:
        async with con.transaction():
            wd_ut = await con.prepare(
                '''update "account_withdraw" set review_status = $1, status=$2, 
                   paid_date=now(), update_date=now() where id = $3''')
            await wd_ut.fetchrow(REVIEW_REJECTED, WITHDRAW_REJECTED, withdraw_id)
            acc_ut = await con.prepare(
                '''update "account" set withdrawing_amount=withdrawing_amount - $1::numeric, 
                   balance_amount = balance_amount + $2::numeric, update_date=now() where id=$3''')
            await acc_ut.fetchrow(amount, amount, account_id)


async def withdraw_agree_account(withdraw_id):
    """审核通过"""
    async with db.conn.acquire() as con:
        async with con.transaction():
            wd_ut = await con.prepare(
                '''update "account_withdraw" set review_status = $1, update_date=now() where id = $2''')
            await wd_ut.fetchrow(WITHDRAW_AGREE, withdraw_id)


async def rejected_user_withdraw(account_id):
    '''指定账户拒绝提现'''
    async def withdraw_statistics(account_id):
        '''单个用户提现统计'''
        async with db.conn.acquire() as con:
            wd_stmt = await con.prepare(
                '''select id, account_id, amount from "account_withdraw"
                   where account_id = $1 and status = $2 and review_status=any($3) 
                   order by account_id, create_date''')
            wd_datas = await wd_stmt.fetch(account_id, WITHDRAWING, [REVIEWING, WITHDRAW_AGREE])
        return wd_datas

    for wd in await withdraw_statistics(account_id):
        await withdraw_rejected_account(wd['account_id'], wd['id'], wd['amount'])
