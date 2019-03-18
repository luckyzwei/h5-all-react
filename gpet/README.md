# 成员
- wen.liu⭐
- jianqiang.li（已离开）
- kefei.zhao
- mengjun.xiang
- miaomiao.yang
- ArisCUI
- zhihui.zhao

# 开发工具（多搜索多研究多看官方文档）
- [IDEA](https://www.jetbrains.com/idea/) 
- [python](https://www.python.org/)
- [sanic](https://github.com/huge-success/sanic)
- [postgresql](https://www.postgresql.org/)
- [redis](https://redis.io/)

# 变更日志 
- 2019-03-05
    - Changes:
        - 移除access.log以及error.log
        - 优化过去15天流水查询sql
        - 新增会话不足注销群原因

- 2019-02-22
    - Changes:
        - 注销因无会话评为一星群
        - 自动退群新增投放开关关闭的群
    - Fixes:
        - 投放开关异常
        - 适配投放主键类型
 
- 2019-02-14
    - Changes:
        - 因结算异常上线走马灯
        - 优化代码
    - Fixes:
        - web群发任务预览换行错误
        - 删除关键字异常

- 2019-01-31
    - Changes:
        - 增加定时任务删除群
        - 优化代码
    - Fixes:
        - 投放小程序异常

- 2019-01-24
    - Changes:
        - 移除一些无用代码
        - 优化目录结构
        - web页面优化
        - 移除图灵功能
    - Fixes:
        - 机器人异常处理
        - 新增结算重复调用问题

- 2019-01-23
    - Changes:
        - 添加打款失败原因说明
        - 微信商家密钥路径修改
        - 更改客服繁忙话术提示
    - Fixes:
        - 修复打款失败bug
        
- 2019-01-21
    - Changes:
        - 项目路径修改
        - 优化cookie存储以及cookie加密处理
        - token时间缩短到1h
        - 投放接口的适配
    - Fixes:
        - 修复首页404bug
        - 修复结算金额bug

# 系统环境
- dev环境
```
https://gpetdev.gemii.cc    http://127.0.0.1:3000
ssh://gpetdev:uH5ZCWdRzNvE62k@52.82.2.37
postgresql://gpetdev:wtXexyYcsf5a2gT@127.0.0.1:2000/gpetdev
redis://127.0.0.1:3030
amqp://gpetdev:vSZ93fpEQPDVV8p@127.0.0.1:2100/gpetdev

链接服务器，需要先本机打隧道，打隧道命令 ssh -qTfnNC -L port1:localhost:port2 user@ip ，
例如打postgresql的隧道 ssh -qTfnNC -L 2000:localhost:2000 user@ip 。

postgresql/git/redis 用 IDEA 内置插件，也可以直接用命令行。
```

- prd环境
```
https://gpetprd.gemii.cc    http://127.0.0.1:3100
```

- op环境（只读）
```
ssh://gpetprdop:PASSWORD@52.82.2.37
postgresql://gpetprdop:PASSWORD@127.0.0.1:2000/gpetprd
```

# mq 队列名称
```
# gpet内部定义的queue名称
queue.pet.point.web    前后端数据埋点推送

# 旁路监听的queue名称
bi.console.gpet.queue  bi监听前后端数据埋点queue    @向阳    
```

# 重要内容整理
## 缓存

- 短链相关(不可手动删除）
```python
SHORTEN_URL_REDIS_KEY = 'GPET:SHORTEN_KEY_IMPORT'               # 短链存储缓存
SHORTEN_CACHE_AWHILE = 'GPET:TMP_SHORT_CACHE:'                  # 短链短暂缓存，以防止生成过多的短链
SHORTEN_COUNTER_REDIS_KEY = 'GPET:SHORTEN_COUNTER_KEY_IMPORT'   # 短链计数缓存
```
- 活跃用户缓存记录(不可手动删除）
```python
USER_OPT_DAY_REDIS_KEY = 'GPET:USER_OPT_{today}'                # 用户操作每日缓存记录,手动删除会造成数据丢失
```

- 机器人分配相关(不可手动删除）
```python
SNAPSHOT_KEY_REDIS_KEY = 'GPET:ROBOT_SNAPSHOT_{today}'          # 机器人表中剩余可激活群数快照
DISTRIBUTE_KEY_REDIS_KEY = 'GPET:ROBOT_DISTRIBUTE_{today}'      # 机器人当日分配数 缓存
DISPLAY_KEY_REDIS_KEY = 'GPET:ROBOT_DISPLAY_{today}'            # 机器人当日展示数 缓存
ACTIVATED_KEY_REDIS_KEY = 'GPET:ROBOT_ACTIVATED_{today}'        # 当日机器人激活群数
```

## 项目重要参数
- 鉴权token采用[jwt](http://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html)认证鉴权，失效时间为1小时

## 项目配置参数
- `MQ_CONFIG`: 外部mq地址
- `INNER_MQ_CONFIG`: 内部mq地址
- `LOCALHOST`: 对外暴露的根域名地址
- `JWT_SECRET`: 鉴权token密钥
- `WX_PAY_KEY`: 微信打款密钥
- `WXPAY_CLIENT_CERT_PATH`: 微信商家证书路径
- `WXPAY_CLIENT_KEY_PATH`: 微信商家密钥路径
- `CAFILE_PATH`: 服务器本地证书
- `ROBOT_HOST`: 机器人项目根域名
- `TULING_APIKEY`: 图灵密钥
- `DISTRIBUTE_AMOUNT`: 机器人每次分配数量
- `DISTRIBUTE_CONFIG`: 机器人每日分配策略
- `DISPLAY_RATE`: 机器人每日展示比率(与分配次数相乘得出总展示次数)
- `FATHER_SETTLE_RATE`: 师傅群结算比率
- `GRAND_FATHER_SETTLE_RATE`: 师爷群结算比率
- `FATHER_AD_SETTLE_RATE`: 师傅广告结算比率
- `GRAND_FATHER_AD_SETTLE_RATE`: 师爷广告结算比率
- `LAUNCH_HOST`: 投放开关接口根域名
- `MD5_SECRET_KEY`: 广告点击收益接口加密密钥

## 返回code码

```python
# 通用code
SERVICE_SUCCESS_CODE = 1200                 # 正常
UNAUTHENTICATE_EXPIRED_CODE = 1406          # 服务器无法根据客户端请求的内容特性完成请求
UNAUTHENTICATE_CODE = 1401                  # 鉴权失败
PARAMS_ERROR_CODE = 1403                    # 请求参数错误
SERVICE_UNAVAILABLE_CODE = 1500             # 服务内部错误
EXTERNAL_INTERFACE_CODE = 1101              # 外部接口调用失败
RESOURCE_NOT_FOUND_CODE = 1404              # 请求资源不存在

# 机器人相关
ROBOT_NOT_ENOUGH_CODE = 1600                # 机器人数量不足
MEM_INFO_FAIL_CODE = 1601                   # 获取群成员信息失败
SEND_MSG_FAIL = 1602                        # 发送消息失败

# 用户信息相关
MISS_PHONE_CODE = 2001                      # 缺失手机号信息
MISS_IDCARD_CODE = 2002                     # 缺失身份证信息
SENSITIVE_WORD_CODE = 2003                  # 用户触发敏感词
CREATED_FAILED_CODE = 2004                  # 创建失败
EXISTS_SAME_TIME_CREATED_CODE = 2005        # 存在同一时间创建记录
COMPLETE_CODE = 2200                        # 用户信息已补全
VERIFY_CODE_WRONG = 2301                    # 验证码错误
VERIFY_CODE_EXPIRE = 2302                   # 验证码过期
PHONE_HAS_REGIST = 2303                     # 手机号已注册
SHORT_MSG_SEND_FREQUENTLY = 2304            # 频繁调用发送短信
EMAIL_MSG_SEND_ERROR = 2401                 # 邮件发送错误
WECHAT_AUTH_ERROR = 2501                    # 微信授权失败

# 账户相关
TRANSFER_FAILED_CODE = 3001                 # 转账失败
INSUFFICIENT_AMOUNT_CODE = 3002             # 账户金额不足
REVOKED_TODAY_CODE = 3003                   # 今日已提现
WITHDRAW_FAILED_CODE = 3004                 # 提现失败
TRANSFER_SUCCESSED = 3200                   # 转账成功
```

## issue
  - [线路图](https://gitlab.com/gemii/gpet/issues/69)
  - [liu.wen研发日志](https://gitlab.com/gemii/gpet/issues/58)
  - [kefei.zhao研发日志](https://gitlab.com/gemii/gpet/issues/59)
  - [jianqiang.li研发日志](https://gitlab.com/gemii/gpet/issues/66)
  - [mengjun.xiang研发日志](https://gitlab.com/gemii/gpet/issues/68)
  - [miaomiao.yang研发日志](https://gitlab.com/gemii/gpet/issues/120)
  - [zhihui.zhao研发日志](https://gitlab.com/gemii/gpet/issues/284)
  - [翻墙指南](https://gitlab.com/gemii/gpet/issues/186)
  - [上线计划](https://gitlab.com/gemii/gpet/issues/161)
  - [pgsql数据库文档](https://gitlab.com/gemii/gpet/issues/122)
  - [压测工具](https://gitlab.com/gemii/gpet/issues/100)
  - [鉴权操作](https://gitlab.com/gemii/gpet/issues/57)
  - [消息队列设计](https://gitlab.com/gemii/gpet/issues/51)
  - [gobot api](https://gitlab.com/gemii/gpet/issues/49)
  - [sanic文档整理](https://gitlab.com/gemii/gpet/issues/25)
  - [项目开发工具及教程](https://gitlab.com/gemii/gpet/issues/24)
  - [遵守规则](https://gitlab.com/gemii/gpet/issues/13)
  - [code码定义](https://gitlab.com/gemii/gpet/issues/72)
  - [后台项目停止开启维护页流程](https://gitlab.com/gemii/gpet/issues/327)
  - [后台项目正常开启维护页流程](https://gitlab.com/gemii/gpet/issues/328)
  - [python速览](https://gitlab.com/gemii/gpet/issues/310)
  - [项目开发git分支使用](https://gitlab.com/gemii/gpet/issues/296)
  - [tmux使用](https://gitlab.com/gemii/gpet/issues/286)
  - [项目部署流程](https://gitlab.com/gemii/gpet/issues/403)
  - [数据埋点需求讨论](https://gitlab.com/gemii/gpet/issues/392)
  - [数据埋点sql汇总](https://gitlab.com/gemii/gpet/issues/413)
  - [前端页面路径汇总](https://gitlab.com/gemii/gpet/issues/156)
  - [前端页面进入逻辑](https://gitlab.com/gemii/gpet/issues/212)
  - [分享汇总和指南](https://gitlab.com/gemii/gpet/issues/459)
 
# 项目部署流程
- 项目环境搭建：
    1. 进入服务器拉取代码：`git clone https://gitlab.com/gemii/gpet.git`
    2. 进入项目根目录，安装python依赖包：`pip install --user -r requirements.txt`
    3. 前端环境安装(nodejs及npm包)：https://github.com/creationix/nvm

- 前端项目运行前准备： 
    1. 安装前端依赖包:
        - 目录 `static/gpet`下运行 `npm install`
        - 目录 `static/gpetmg`下运行 `npm install`

    2. gpetmg前端项目`node_modules`中源码修改处:
        - 文件路径1：`static/gpetmg/node_modules/react-scripts/config/paths.js`
            - **修改**`const envPublicUrl = '/gpetmg'`

    3. webpack打包前端项目为静态文件：
        - 目录 `static/gpet`下运行 `npm run build`
        - 目录 `static/gpet`下运行 `npm run build`

- 后端项目运行前准备：
    1. 添加`config.py`配置文件(根据不同环境添加不同的配置)


- 项目启动：
    - web项目启动：
        1. 使用tmux作为后台启动方式 #200 #286
        2. 进入tmux session: `tmux new -s pet_web`
        3. 运行web项目：`python3 gpet_run.py`
        4. 退出session(进入后台模式)：`ctrl+b d`
    - scheduler定时任务启动：
        1. 使用tmux作为后台启动方式 #200 #286
        2. 进入tmux session: `tmux new -s sche`
        3. 运行web项目：`python3 schedule_tasks.py`
        4. 退出session(进入后台模式)：`ctrl+b d`


# 项目版本迭代发布流程
- 书写变更日志
- 梳理项目发布前的准备事项(发布issue)
- 根据发布注意事项内容在服务器上进行发布
- 线上测试