# ========= 接口相关 ========== #
import os
BASIC_PATH = os.path.abspath(os.path.dirname(__name__))  # 当前路径地址

SERVICE_SUCCESS_CODE = 1200  # 正常
UNAUTHENTICATE_EXPIRED_CODE = 1406  # 服务器无法根据客户端请求的内容特性完成请求
UNAUTHENTICATE_CODE = 1401  # 鉴权失败
PARAMS_ERROR_CODE = 1403  # 请求参数错误
SERVICE_UNAVAILABLE_CODE = 1500  # 服务内部错误
EXTERNAL_INTERFACE_CODE = 1101  # 外部接口调用失败
RESOURCE_NOT_FOUND_CODE = 1404  # 请求资源不存在
DUPLICATE_REQUEST_CODE = 1409   # 请求冲突，重复调用

# 机器人相关
ROBOT_NOT_ENOUGH_CODE = 1600  # 机器人数量不足
MEM_INFO_FAIL_CODE = 1601  # 获取群成员信息失败
SEND_MSG_FAIL = 1602  # 发送消息失败

# 用户信息相关
MISS_PHONE_CODE = 2001  # 缺失手机号信息
MISS_IDCARD_CODE = 2002  # 缺失身份证信息
SENSITIVE_WORD_CODE = 2003  # 用户触发敏感词
CREATED_FAILED_CODE = 2004  # 创建失败
EXISTS_SAME_TIME_CREATED_CODE = 2005  # 存在同一时间创建记录
COMPLETE_CODE = 2200  # 用户信息已补全
VERIFY_CODE_WRONG = 2301  # 验证码错误
VERIFY_CODE_EXPIRE = 2302  # 验证码过期
PHONE_HAS_REGIST = 2303  # 手机号已注册
SHORT_MSG_SEND_FREQUENTLY = 2304  # 频繁调用发送短信
EMAIL_MSG_SEND_ERROR = 2401  # 邮件发送错误
WECHAT_AUTH_ERROR = 2501  # 微信授权失败

# 账户相关
TRANSFER_FAILED_CODE = 3001  # 转账失败
INSUFFICIENT_AMOUNT_CODE = 3002  # 账户金额不足
REVOKED_TODAY_CODE = 3003  # 今日已提现
WITHDRAW_FAILED_CODE = 3004     # 提现失败
TRANSFER_SUCCESSED = 3200  # 转账成功

# ========= REDIS相关 =========== #

# 独立REDIS_KEY
CUSTOMER_SESSION_REDIS_KEY = 'GPET:CUSTOMER_MESSAGE_{user_code}'  # 用户阿里云客服队列
CUSTOMER_SUCCESS_SESSION_REDIS_KEY = 'GPET:CUSTOMER_SUCCESS:SESSION_{user_code}'  # 用户接入阿里云客服成功
TIMING_NOTICE_STAR_REDIS_KEY = 'GPET:TIMING_NOTICE_STAR'  # 定时发送提示星级内容缓存redis_key
SEND_MSG_VAL_REDIS_KEY = 'GPET:SMS:VERIFY_CODE_{user_id}_{phone}'  # 手机号验证码缓存
SEND_MSG_RATE_REDIS_KEY = 'GPET:SMS:MSG_RATE_{user_id}'  # 发送短信频率缓存
TASK_SEND_RESULT_REDIS_KEY = 'GPET:TASK_SEND_{resource_id}'  # 投放系统投放任务缓存，记录投放对应的群和发送状态
OPEN_ACCESSTOKEN_REDIS_KEY = 'GPET:WECHAT_OPEN_ACCESSTOKEN'  # 开放平台redis缓存
JS_API_TICKET_REDIS_KEY = 'GPET:WX_JSAPI_TICKET_{app_id}'  # 用户分享ticket
GPET_WORLD_ACCESS_TOKEN_REDIS_KEY = 'GPET:WORLD_ACCESSTOKEN_{app_id}'  # 微小宠world公众号access_token缓存
GPET_ROBOT_ADD_FRIEND_REDIS_KEY = 'GPET_ROBOT_ADD_FRIEND_{user_code}_{robot_code}'  # 机器人加好友锁
NO_CLICK_GROUPS_REDIS_KEY = 'GPET:NO_CLICK_GROUPS_{today}'  # 无点击群列表缓存

GROUP_WELCOME_MSG_RECORD_REDIS_KEY = 'GPET:GROUP_WELCOME_MSG_RECORD'      # 触发群欢迎语
# 私聊消息事务相关
TASK_MSG_MONITOR_REDIS_KEY = 'GPET:TASK_MESSAGE_MONITOR'  # 群发任务创建后定时发送缓存
MASS_MSG_TASK_CREATE_REDIS_KEY = 'GPET:TASKS:{task_id}'  # 创建群发消息任务缓存
MASS_MESSAGE_TRANC_REDIS_KEY = 'GPET:MASS_MESSAGE_{mem_code}_{robot_code}'  # 群发消息事务
CUSTOMER_MESSAGE_TRANC_REDIS_KEY = 'GPET:CUSTOMER_MESSAGE_{mem_code}'  # 客服消息事务
# 短链相关
SHORTEN_URL_REDIS_KEY = 'GPET:SHORTEN_KEY_IMPORT'   # 短链存储缓存
SHORTEN_CACHE_AWHILE = 'GPET:TMP_SHORT_CACHE:'      # 短链短暂缓存，以防止生成过多的短链
SHORTEN_COUNTER_REDIS_KEY = 'GPET:SHORTEN_COUNTER_KEY_IMPORT'   # 短链计数缓存

USER_CODE_ID_MAP_REDIS_KEY = 'GPET:USER_CODE_ID_MAP'    # 用户id和code对应缓存
USER_UNION_ID_MAP_REDIS_KEY = 'GPET:USER_UNION_ID_MAP'  # 用户id和code对应缓存
USER_OPT_DAY_REDIS_KEY = 'GPET:USER_OPT_{today}'        # 用户操作每日缓存记录

# 通用REDIS_KEY
USER_ACCOUNT_REDIS_KEY = 'GPET:USER_ACCOUNT_MAP'                          # user_code与account_id缓存
SNAPSHOT_KEY_REDIS_KEY = 'GPET:ROBOT_SNAPSHOT_{today}'                    # 机器人表中剩余可激活群数快照
DISTRIBUTE_KEY_REDIS_KEY = 'GPET:ROBOT_DISTRIBUTE_{today}'                # 机器人当日分配数 缓存
DISPLAY_KEY_REDIS_KEY = 'GPET:ROBOT_DISPLAY_{today}'                      # 机器人当日展示数 缓存
ACTIVATED_KEY_REDIS_KEY = 'GPET:ROBOT_ACTIVATED_{today}'                  # 当日机器人激活群数
GROUP_USER_ROBOT_MAP_REDIS_KEY = 'GPET:GROUP_USER_ROBOT_MAP'              # 群对应的 robot group user 信息
STATISTICS_USER_GROUPS_REDIS_KEY = 'GPET:STATISTICS_USER_GROUPS_{today}'  # 群数据统计 进群/入群人数，群内发言人数
KEYWORD_KEY_REDIS_KEY = 'GPET:GROUP:KEYWORDS'                             # 群对应的关键字缓存
SUB_EXPIRE_REDIS_KEY = '__keyevent@0__:expired'                           # 检测缓存中失效的key
ROBOT_BLOCKED_REDIS_KEY = 'GPET:ROBOT_BLOCKED_GROUPS_{robot_code}'  # 机器人封号缓存用户与群

# 徒弟唤醒设置缓存当日只能提醒一次
APPRENTICE_REMID_REDIS_KEY = 'GPET:APPRENTICE_REMIND'
# 用户的师傅、师爷关系缓存 --> 用于BI数据查询时
COMPLETE_USER_REDIS_KEY = 'GPET:USER_RELATESHIPS'
# 成员信息
GROUP_MEMBER_INFO_REDIS_KEY = 'GPET:GROUP_MEMBER_INFO:'

# ========== 类型相关 ========= #


class MSGTYPE:
    '''消息类型'''
    TEXT = 3
    IMAGE = 8
    LINK = 6
    MINI_PROGRAM = 11
    USER_CARD = 12


class TYPE:
    '''账户流水类型'''
    PULL_GROUP = 1
    AD_CLICK = 2
    SUB_PULL_GROUP = 3
    SUB_AD_CLICK = 4
    ACTIVITY = 5
    ADOPTION = 8
    WITHDRAW = 9
    OTHER = 10


class UserOpt:
    '''用户操作类型'''
    ACTIVE = 1


class GroupCancelReason:
    """群注销原因"""
    ILLEGAL = 1  # 违法群
    LAUNCH_LOW = 2  # 投放质量较差
    ROBOT_KICKED = 3  # 机器人退群
    SYSTEM_ACTIVE = 4  # 系统主动注销
    STAR_LOW_LIMIT = 5  # 低星级限制
    ROBOT_BLOCKED = 6  # 机器人封号
    SESSION_LOW_LIMIT = 7  # 会话不足


# ========== 定义QUEUE地址相关 ========== #


POINT_WEB_QUEUE_NAME = 'queue.pet.point.web'
