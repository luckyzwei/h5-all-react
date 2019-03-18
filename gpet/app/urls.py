import os

from sanic import Blueprint
from sanic.exceptions import FileNotFound
from sanic.response import file

from app import route_account, route_app, route_admin, route_costomer_msg, route_group, route_group_star, route_launch, \
    route_mass_message, route_poster, route_robot, route_shorten, route_to_bi, route_user, wechat_auth, route_shortmsg
from ut.constants import BASIC_PATH
import schedule_tasks

bp = Blueprint('pet_blueprint')


async def static_route(request, path=''):
    file_path = os.path.join(BASIC_PATH, 'static/gpet/build/index.html')
    try:
        return await file(file_path)
    except Exception:
        raise FileNotFound('File not found', path=file_path, relative_url=None)


async def admin_static_route(request, str):
    file_path = os.path.join(BASIC_PATH, 'static/gpetmg/build/index.html')
    try:
        return await file(file_path)
    except Exception:
        raise FileNotFound('File not found', path=file_path, relative_url=None)


bp.add_route(route_account.user_incomes_view, '/profit')
bp.add_route(route_account.user_incomes_detail_view, '/profit/slip')
bp.add_route(route_account.user_withdraw_view, '/withdraw')
bp.add_route(route_account.user_withdraw_request_view, '/withdraw', methods=['POST'])
bp.add_route(route_account.change_withdraw_record, '/withdraw/review', methods=['POST'])

bp.add_route(route_app.check_app_status, '/app/status', methods=['GET'])
bp.add_route(route_app.set_app_status, '/app/status', methods=['POST'])
bp.add_route(route_app.webpage_access_view, '/page/access')
bp.add_route(route_app.get_marquee_info, '/app/marquee', methods=['GET'])
bp.add_route(route_app.set_marquee_info, '/app/marquee', methods=['POST'])

bp.add_route(route_admin.withdraw_list_admin, '/admin/withdraw', methods=['POST'])
bp.add_route(route_admin.export_result, '/admin/withdraw/export', methods=['POST'])
bp.add_route(route_admin.problem_feedback, '/admin/problem/feedback', methods=['POST'])
bp.add_route(route_admin.problem_feedback_export, '/admin/problem/feedback/export', methods=['POST'])
bp.add_route(route_admin.get_problem_category, '/admin/problems')

bp.add_route(route_costomer_msg.customer_msg_callback, '/aliyun/callback', methods=['POST'])

bp.add_route(route_group.get_group_list, '/groups')
bp.add_route(route_group.modify_robot_nickname, '/groups/<group_code:[a-z-A-Z-0-9\\-]+>/robot_name', methods=['PUT'])
bp.add_route(route_group.group_statistic, '/groups/statistics')
bp.add_route(route_group.update_group_welcome_msg, '/groups/<group_id:[a-z-A-Z-0-9\\-]+>/welcome', methods=['POST'])
bp.add_route(route_group.group_welcome_msg, '/groups/welcome')
bp.add_route(route_group.owner_group_verify, '/owner/group/verify')
bp.add_route(route_group.get_owner_group, '/owner/groups')
bp.add_route(route_group.delete_groups, '/groups/delete', methods=['POST'])
bp.add_route(route_group.delete_group, '/group/<group_id:[a-zA-Z0-9\\-]+>', methods=['DELETE'])
bp.add_route(route_group.exception_group_pull, '/pullback/<group_id:[a-zA-Z0-9\\-]+>', methods=['GET'])

bp.add_route(route_group_star.group_star, '/groups/star', methods=['POST'])

bp.add_route(route_launch.launch_switch, '/launch/switch', methods=['PUT'])
bp.add_route(route_launch.launch_history, '/launch/history')
bp.add_route(route_launch.launch_history_detail, '/launch/history/detail')
bp.add_route(route_launch.receive_task, '/task/receive', methods=['POST'])
bp.add_route(route_launch.no_click_groups, '/groups/no_click', methods=['POST'])

bp.add_route(route_mass_message.enter_mass_task_view, '/tasks/<task_id:[a-zA-Z0-9\\-]+>')
bp.add_route(route_mass_message.completion_task_view, '/tasks/<task_id:[a-zA-Z0-9\\-]+>', methods=['PUT'])
bp.add_route(route_mass_message.mass_message_task_view, '/tasks/messages')
bp.add_route(route_mass_message.mass_message_detail_view, '/tasks/<task_id:[a-zA-Z0-9\\-]+>/message')
bp.add_route(route_mass_message.mass_message_detele_view, '/tasks/<task_id:[a-zA-Z0-9\\-]+>', methods=['DELETE'])

bp.add_route(route_poster.user_share_poster, '/user/<user_id:[a-zA-Z0-9\\-]+>/poster', methods=['GET'])
bp.add_route(route_poster.init_poster, '/gpet/poster', methods=['GET'])
bp.add_route(route_poster.store_image_handler, '/poster/background', methods=['POST'])

bp.add_route(route_robot.robot_distribution_view, '/robot/distribution', methods=['POST'])
bp.add_route(route_robot.robot_undistributable_view, '/robot/undistributable', methods=['POST'])

bp.add_route(route_shorten.redirect_to_long, '/s/<short:[a-zA-Z0-9\\-]+>')
bp.add_route(route_shorten.long_to_short_view, '/long_to_short', methods=['POST'])

bp.add_route(route_to_bi.users_info, '/bi/users', methods=['POST'])
bp.add_route(route_to_bi.users_statistic_view, '/settlement', methods=['POST'])

bp.add_route(route_user.get_user_id, '/user')
bp.add_route(route_user.modify_user, '/user/<user_id:[a-zA-Z0-9\\-]+>', methods=['PUT'])
bp.add_route(route_user.is_receive_redpacket, '/received/redpacket', methods=['GET'])
bp.add_route(route_user.receive_redpacket, '/receive/redpacket', methods=['GET'])
bp.add_route(route_user.modify_user_phone, '/user/phone', methods=['PUT'])
bp.add_route(route_user.isregister, '/users/<union_id:[a-zA-Z0-9\\_-]+>/registered', methods=['GET'])
bp.add_route(route_user.block_user, '/users/<user_id:[a-zA-Z0-9\\-]+>/block', methods=['PUT'])
bp.add_route(route_user.is_bolcked, '/users/block_verify')
bp.add_route(route_user.get_now_distribute_robot, '/robot/show')
bp.add_route(route_user.get_user_apprentice, '/user/apprentice')
bp.add_route(route_user.apprentice_remind, '/apprentice/awakening', methods=['POST'])
bp.add_route(route_user.get_user_distribute_robots, '/user/robots')
bp.add_route(route_user.get_problem_category, '/problems')
bp.add_route(route_user.save_user_problem, '/user/problem', methods=['POST'])
bp.add_route(route_user.get_alt_msg, '/alt_msg')
bp.add_route(route_user.get_msg_context, '/groups/<group_code:[A-Z0-9\\-]+>/msg/<msg_id:[a-zA-Z0-9\\-]+>/context')
bp.add_route(route_user.send_alt_msg, '/alt_msg/reply', methods=['POST'])
bp.add_route(route_user.get_user_groups_disciples, '/user/groups/disciples')
bp.add_route(route_user.modify_user_identity, '/user/idcard', methods=['PUT'])
bp.add_route(route_user.refresh_user, '/user/refresh/<union_id:[a-zA-Z0-9\\_-]+>', methods=['PUT'])
bp.add_route(route_user.alt_switch, '/alt/switch', methods=['PUT'])
bp.add_route(route_user.alt_switch_info, '/alt/switch')
bp.add_route(route_user.keyword_list, '/keywords', methods=['GET'])
bp.add_route(route_user.keyword_detail, '/keywords/<id:[a-z-A-Z-0-9\\-]+>', methods=['GET'])
bp.add_route(route_user.create_keyword, '/keywords', methods=['POST'])
bp.add_route(route_user.modify_keyword, '/keywords', methods=['PUT'])
bp.add_route(route_user.delete_keyword, '/keywords', methods=['DELETE'])

bp.add_route(route_shortmsg.send_msg_batch, '/sms/delivery/batch', methods=['POST'])
bp.add_route(route_shortmsg.send_verify_code, '/sms/code/delivery', methods=['GET'])

bp.add_route(wechat_auth.wechat_user_info, '/wechat/user_info', methods=['GET'])
bp.add_route(wechat_auth.js_api_ticket, '/wechat/js/ticket', methods=['GET'])

# ===== 静态文件 ===== #

bp.add_route(admin_static_route, '/gpetmg/<str>')
bp.add_route(static_route, '/grouppet/<path:path>')
bp.static('/js', os.path.join(BASIC_PATH, 'static/gpet/build/js'))
bp.static('/static', os.path.join(BASIC_PATH, 'static/gpet/build/static'))
bp.static('/images', os.path.join(BASIC_PATH, 'static/gpet/build/images'))
# bp.static('/css', os.path.join(BASIC_PATH, 'static/gpet/build/css'))
bp.static('/gpetmg/static', os.path.join(BASIC_PATH, 'static/gpetmg/build/static'))
bp.static('/gpetmg/images', os.path.join(BASIC_PATH, 'static/gpetmg/build/images'))
bp.static('/gpetmg/css', os.path.join(BASIC_PATH, 'static/gpetmg/build/css'))
