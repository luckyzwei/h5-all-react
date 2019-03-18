- 公共接口
	- [1. 微信授权](#微信授权)
	- [2. 微信获取分享ticket](#微信获取分享ticket)
	- [3. 校验当前服务状态](#校验当前服务状态)
	- [4. 设置当前服务状态](#设置当前服务状态)
	- [5. 发送短信验证码](#发送短信验证码)
	- [6. 批量发送短信](#批量发送短信)
	- [7. 长链转短链](#长链转短链)
	- [8. 获取token](#获取token)
	- [9. 批量注销群](#批量注销群)
	- [10. 用户封号](#用户封号)
	- [11. 将机器人置为不可分配](#不可分配)
	- [12. 首页跑马灯状态和内容](#首页跑马灯状态和内容)
    - [13. 设置首页跑马灯内容和状态](#设置首页跑马灯内容和状态)
- web接口
    - [1.获取用户当前绑定机器人](#获取用户当前绑定机器人)
    - 用户群、徒弟徒孙信息
        - [2.首页获取群数量和徒弟徒孙数量](#首页获取群数量和徒弟徒孙数量)
        - [3.用户群列表](#用户群列表)
        - [4.修改机器人在群内昵称](#修改机器人在群内昵称)
        - [5.徒弟徒孙列表](#徒弟徒孙列表)
        - [6.唤醒徒弟](#唤醒徒弟)
    - 用户群主群
        - [7.用户是否有群主群](#用户是否有群主群)
        - [8.群主群列表](#群主群列表)
    - 群欢迎语
        - [9.查询用户群欢迎语](#查询用户群欢迎语)
        - [10.修改用户群欢迎语](#修改用户群欢迎语)
    - 群关键字
        - [11.新增关键字](#新增关键字)
        - [12.修改关键字](#修改关键字)
        - [13.删除关键字](#删除关键字)
        - [14.查询关键字列表](#查询关键字列表)
        - [15.关键字详情](#关键字详情)
    - @消息
        - [16.获取@消息通知开关](#获取@消息通知开关)
        - [17.设置@消息通知开关](#设置@消息通知开关)
        - [18.@消息列表](#@消息列表)
        - [19.@消息上下文](#@消息上下文)
    - 问题反馈
        - [20.获取用户已分配的机器人列表](#用户已分配的机器人列表)
        - [21.获取问题列表](#获取问题列表)
        - [22.反馈问题](#反馈问题)
    - 用户基本信息
        - [23.用户是否封号](#用户是否封号)
        - [24.获取用户user_id](#获取用户user_id)
        - [25.用户是否注册](#用户是否注册)
        - [26.补全用户信息](#补全用户信息)
        - [27.补全用户手机号](#补全用户手机号)
        - [28.补全身份证信息](#补全身份证信息)
    - 投放
        - [29.设置投放开关](#设置投放开关)
        - [30.投放历史](#投放历史)
        - [31.投放历史详情](#投放历史详情)
        - [32.分配机器人](#分配机器人)  
    - 收益
        - [33.用户收益概览](#用户收益)
        - [34.每日收益明细](#每日收益明细)
        - [35.提现接口](#提现接口)
        - [36.确认提现接口](#确认提现接口)
   - 群发消息
        - [37.进入群发消息补全页面](#进入群发消息补全页面)
        - [38.更新群发消息](#更新群发消息)
        - [39.群发消息列表页](#群发消息列表页)
        - [40.群发消息详情](#群发消息详情)
        - [41.群发消息撤回](#群发消息撤回)
   - 鉴权
        - [42.获取当前token的用户ID](#获取当前token的用户ID)

- web后台接口
    - 提现
        - [提现列表](#提现列表)
    - 问题反馈
        -[后台问题反馈列表](#后台问题反馈列表)
   

        
- 外部系统调用接口
	- [1. 阿里云客服回调](#阿里云客服回调)
	- [2. 群星级评定](#群星级评定)
	- [3. 群投放](#群投放)
	- [锚点1](#item_out_1)
	- [锚点1](#item_out_1)
- [错误码对照表](#错误码对照表)



### 公共接口
#### 微信授权

**请求地址**
>GET /wechat/user_info?app_id=1234&code=1234
	
**请求参数**
> 无
	
**返回示例**
	
```
{
	"code": 1200,
	"description": "",
	"data": {
		"openid": "ocSwr1DzWi0mKa27riXAPW3s3wjw",
		"nickname": "请叫我小稳稳",
		"sex": 1,
		"language": "zh_CN",
		"city": "蚌埠",
		"province": "安徽",
		"country": "中国",
		"headimgurl": "http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKONsO37xAqEuQbTYendndpfbd0KFFgDIsY4wFDSa22K8KXGiaqqL5porTLZN2MAI2bBG9pFgpcSow/132",
		"privilege": [],
		"unionid": "oVzypxARc1pEsaCS9D5UxKpQPrpc"
	}
}
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
openid | string | Y | 对于微信公众号唯一标识
nickname | string | Y | 昵称
sex | int | Y | 性别
language | string | Y | 语言
city | string | Y | 城市
province | string | Y | 省份
country | string | Y | 国家
headimgurl | string | Y | 头像
privilege | string | Y | 特权，一般为[]
unionid | string | Y | 微信授权唯一标识
		
---

#### 微信获取分享ticket

**请求地址**
>GET /wechat/js/ticket?app_id=1234&url=1234
	
**请求参数**
> 无
	
**返回示例**
	
```
{
	"code": 1200,
	"description": "",
	"data": {
		"appid": "",
		"timestamp": "",
		"noncestr": "",
		"signature": ""
	},
	"page_info": {}
}
```

**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
appid | string | Y | 微信公众号唯一标识
timestamp | string | Y | 时间戳，用作加密用
noncestr | string | Y | 签名随机字符串
signature | string | Y | 用sha1算法生成的加密签名

---

#### 校验当前服务状态
	
**请求地址**
>GET /app/status
	
**请求参数**
> 无
	
**返回示例**
	
```
 {
     "code": 1200,
     "description": "",
     "data": {
         "status": 1,
         "upGradeEndTime": "11月14日19点"
     },
     "page_info": {}
 }
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 1代表服务正常 2代表服务维护
upGradeEndTime | string | N | 当status=2时，取此值进行展示

--- 

#### 设置当前服务状态
	
**请求地址**
>POST /app/status
	
**请求参数**
	
```
{
    "status": 1,
    "upGradeEndTime": "12月17日12点"
}
```

**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 1代表服务正常 2代表服务维护
upGradeEndTime | string | N | 当status=2时，页面维护时间取此值进行展示
	
**返回示例**
	
```
 {
     "code": 1200,
     "description": "",
     "data": {
         "status": 1,
         "upGradeEndTime": "11月14日19点"
     },
     "page_info": {}
 }
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 1代表服务正常 2代表服务维护
upGradeEndTime | string | N | 当status=2时，页面维护时间取此值进行展示

---

#### 发送短信验证码
	
**请求地址**
>GET /sms/code/delivery
	
**请求参数**
>无
	
**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": null,
     "page_info": {}
 }

```
**返回参数说明**
	
>  无
	
---

#### 批量发送短信

**请求地址**
>POST /sms/delivery/batch
	
**请求参数**
	
```
{
    "phones": ["152xxxx1234", "152xxxx1234"],
    "content": "...."
}
```
**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
phones | List | Y | 需要发送短信的手机号列表
content | string | Y | 短信内容

	
**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": null,
     "page_info": {}
 }
	
```
---

#### 长链转短链
	
**请求地址**
>POST /long_to_short
	
**请求参数**
	
```
{
    "url": ""
}
```
**请求参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
url | string | Y | 要转成短链的url

	
**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": "",
     "page_info": {}
 }
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data | string | Y | 长链转化后的短链
---

#### 获取token
	
**请求地址**
>POST /auth
	
**请求参数**
	
```
{
    "union_id": ""
}
```
**请求参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
union_id | string | Y | 微信账号唯一标识
	
**返回示例**
	
```
	{
		"code": 1200,
		"msg": "",
		"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMjk0OGFhYmUtZDM5NC00Y2YzLTllODgtYTI1NDM5M2Q1NDEwIiwiZXhwIjoxNTQ3NzM2NzczfQ.a06m_DbgPQvncJ3CngnZXLsjiqc3GVlfzmPjyzJKIT8"
	}
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
access_token | string | Y | 鉴权必须要携带在请求头的参数

---

#### 批量注销群
**请求地址**
>POST /groups/delete
	
**请求参数**
	
```
{
    "group_ids": ["", ""],
    "cancel_reason": 4
}
```
**请求参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
group_ids | List | Y | 注销群列表
cancel_reason | int | N | 1: 违法 2: 投放质量差 3: 机器人被T 4: 系统注销 5：低星级超过限制 6: 机器人封号

**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": "",
     "page_info": {}
 }
	
```
**返回参数说明**
>  无
---

#### 用户封号
**请求地址**
>PUT /users/{user_id}/block

**请求参数**
> 无
	
**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": "",
     "page_info": {}
 }
	
```

**返回参数说明**
	
>  无
---

#### 将机器人置为不可分配
**请求地址**
>POST /robot/undistributable

**请求参数**
```
{
	"robot_id": ""
}

```
	
**返回示例**
	
```
{
     "code": 1200,
     "description": "",
     "data": "",
     "page_info": {}
 }
	
```

**返回参数说明**
	
>  无

#### 首页跑马灯状态和内容
	
**请求地址**
>GET /app/marquee
	
**请求参数**
> 无
	
**返回示例**
	
```
{
    "code": 1200,
    "description": "",
    "data": {
        "status": 1,
        "content": "亲爱的小宠主人，由于小宠结算系统异常，导致小宠提现失败，预计本周修复，在此期间请勿提现操作，还请诸位谅解！"
    }
}
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 是否开启跑马灯 1 开启 0 关闭
content | string | Y | 跑马灯展示内容

--- 

#### 设置首页跑马灯内容和状态
	
**请求地址**
>POST /app/marquee
	
**请求参数**
	
```
{
    "status": 1,
    "content": ""
}
```

**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 是否开启跑马灯 1 开启 0 关闭
content | string | Y | 跑马灯展示内容
**返回示例**
	
```
{
    "code": 1200,
    "description": "",
    "data": "SUCCESS"
}
	
```
**返回参数说明**
	
> 无
	
### web接口


####  获取用户当前绑定机器人
	
**请求地址**
>GET  /robot/show

**鉴权方式**
> token 鉴权

**请求参数说明** 
> 无

**返回参数**
	
```
{
    "code": 1200,
    "description": "",
    "data": {
        "robot_id": string,
        "robot_name": string,
        "qr_code": string,
        "head_url": string,
        "wechat_no": "vnIxRUxcxsn"
    }
}
```

**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
robot_id | string | Y | robot_id
robot_name | string | Y | 机器人名字
qr_code | string | Y | 机器人二维码
head_url | string | Y | 机器人头像
wechat_no | string | Y | 机器人微信号
---



#### 首页获取群数量和徒弟徒孙数量
	
**请求地址**
>GET  /user/groups/disciples
	
**鉴权方式**
> token 鉴权

**请求参数说明** 
> 无

**返回示例**
	
```
{
    "code": 1200,
    "description": "",
    "data": {
        "group_count": 1,    // 群数量
        "disciples": 6,      //  徒弟徒孙总数
    }
}
```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
group_count | int | Y | 群数
disciples | int | Y | 徒弟徒孙总数
---

#### 用户群列表
	
**请求地址**
>GET /groups?status= &current_page= & page_size=

**鉴权方式**
> token 鉴权
	
**请求参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
status | int | Y | 1 已同步 0 待同步
current_page | int | N | 请求页数
page_size | int | N | 每页大小

**返回示例**
	
```
{
    "code": int,
    "description": string,
    "data": [
      {
        "code": "",                  // 群code
        "name": "测试群啊",           // 群名字         
        "settle_count": 31,          // 结算天数
        "quality_level": 2,          // 群星级
        "robot_name": "小熊英英",     // 机器人在群名称
        "launch_switch": 0,          // 投放开关 0 关 1 开
        "create_date": "2018-11-22", // 群创建时间
        "income_status": "",         // 收益状态
        "group_income": 1.5,         // 群收益
        "text_income": 0.16          // 文章收益
        "old_group": int,            // 判断新群和老群 0 新群 1 老群
    },
     ],
    "page_info": {}
}
	
```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
code |string | Y | 群code
name | string | Y | 群名字
create_date |string | Y | 群创建时间
settle_count | int | N | 结算天数
quality_level | int | N | 群星级
robot_name |string | N | 机器人在群名称
launch_switch | int | N | 投放开关 0 关 1 开
income_status |string | N | 收益状态
group_income | int | N | 群收益
text_income | int | N | 文章收益
old_group | int | N | 是否新群 0 新群 1 老群

---

#### 修改机器人在群内昵称
	
**请求地址**
>POST  /groups/:group_id/robot_name
	
**鉴权方式**
> token 鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
remark_name |string | Y | 机器人在群内昵称

**返回示例**
	
```
{
   "code": int,
   "description": string,
   "data": "SUCCESS"
 }
 

```
**返回参数说明** 
>  无
---

#### 徒弟徒孙列表
	
**请求地址**
>GET /user/apprentice?lelave= &current_page= &page_size=

**鉴权方式**
> token 鉴权

**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
leave | int | Y | 1 徒弟列表 2 徒孙列表
current_page | int | N | 请求页数
page_size | int | N | 每页大小

**返回示例**
	
```
{
    "code":int,        //1200：正常
    "data": [
        {
        "is_import":boolean ,         //是否导群true已导群
        "is_apprentice":booleanm,     //是否收徒,true已收徒
        "create_date":string,         //创建时间
        "name":,		      //用户昵称,
        "user_id":	              //用户id
    }
             ],
    "description":"描述",
    
    "page_info": {
        "current_page": 0,
        "page_size": 20,
        "total_page": 1,
        "total_records": 5
    }
}
```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
is_import |boolean | Y | 是否导群 true已导群
is_apprentice | boolean | Y | 是否收徒,true已收徒
create_date |string | Y | 创建时间
name | string | Y | 用户昵称
user_id | string | Y | 用户id
---

#### 唤醒徒弟
	
**请求地址**
>POST /apprentice/awakening

**鉴权方式**
> token 鉴权

**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
is_import | boolean | Y | 导群唤醒
is_apprentice | boolean | Y | 收徒唤醒

**请求示例**
```
{
    "is_import": True,
    "is_apprentice" : False
}
```

**返回示例**
	
```
{
  	"code":int,        //1200：正常 1404:机器人未找到
  	"data": None,
  	"description":"描述"
}

```
**返回参数说明**
>  无
---

#### 用户是否有群主群
	
**请求地址**
>GET /owner/group/verify
	
**鉴权方式**
> token 鉴权

**请求参数说明**
>  无

**返回示例**
```
{
     "code":int,        //1200：成功 1404：用户不存在
     "data":           // False 没有群主群，True 有群主群
     "description":"描述"
}

```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data | boolean | Y | False 没有群主群，True 有群主群
---

#### 群主群列表
	
**请求地址**
>GET /owner/groups?current_page= &page_size=

**鉴权方式**
> token 鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page | int | N | 请求页数
page_size | int | N | 每页大小  -1，需要获取所有数据，不分页,此时必传

**返回示例**
```
{
	"code":int,        //1200：成功 1404：用户不存在
  	"data": [
  		{
            "id": "",                            // 群ID
            "code": "",                          // 群code
            "name": "未命名",                     // 群name
            "launch_switch": 1,
            "create_date": "2018-01-01 15:55:12"  // 群创建时间
        }
  	]
  	"description":"描述",
	"page_info": {
        "current_page": 0,
        "page_size": 20,
        "total_page": 1,
        "total_records": 1
    }
}

```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id | string | Y | 群ID
code |string | Y | 群code
name |string | Y | 群name
launch_switch |int| Y | 群投放开关
create_date |string | Y | 群创建时间
---

#### 群主群数据
	
**请求地址**
>GET groups/statistics?current_page= &page_size=

**鉴权方式**
> token 鉴权
	
**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page | int | N | 请求页数
page_size | int | N | 每页大小

**返回示例**
```
{
    "code": int,
    "description": string,
    "data": [
        {
        "group_id": string,         // 群id
        "group_name": null,         // 群名字
        "group_mem_counts": int,    // 群成员数
        "join_group_counts": int,   // 进群人数
        "exit_group_counts": int,   // 退群人数
        "speaker_counts": int       // 群内发言人数
    }
    ],
    
    "page_info": {
    "current_page": 0,
    "page_size": 5,
    "total_page": 1,
    "total_records": 3
        }
}
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
group_id |string | Y | 群id
group_name | string | Y| 群名字
group_mem_counts |int | Y| 群成员数
join_group_counts |int | Y| 进群人数
exit_group_counts |int | Y| 退群人数
speaker_counts |int | Y| 群内发言人数
---

#### 查询用户群欢迎语
	
**请求地址**
>GET /groups/welcome?current_page= &page_size=
	
**鉴权方式**
> token 鉴权
	
**请求参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page | int | N | 请求页数
page_size | int | N | 每页大小

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": [
        {
            "id": "524f6c03-f507-4535-82f1-a949fb6c2bd3",
            "name": "未命名",
            "welcome_msg": "欢迎1"
        }
    ],
    "page_info": {
        "current_page": 0,
        "page_size": 10,
        "total_page": 1,
        "total_records": 3
    }
}
	
```
**返回参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id |string | Y | 群id
name | string | Y| 群名字
welcome_msg |string | Y| 群欢迎语
---


#### 修改用户群欢迎语
	
**请求地址**
>POST /groups/:group_id/welcome

**鉴权方式**
> token 鉴权
	
**请求参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
welcome_msg | string | Y | 群欢迎语
**请求示例**
```
{
    "welcome_msg":"欢迎入群"
}
```

**返回示例**
```
{
     "code": int,               1200 成功   2003 检测到敏感词汇
     "description": string,
     "data": "SUCCESS"
}
```
**返回参数说明**
>  无
---


#### 新增关键字
	
**请求地址**
>POST /keywords

**鉴权方式**
> token 鉴权
	
**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
group_codes | list-string | Y | 关键字对应的group_code,多个用 ,隔开
keywords | list-string | Y | 关键字，多个用,隔开
reply_content | string | Y | 触发关键字回复内容

**请求示例**
```
{
    "group_codes":["",""],
    "keywords": ["", ""],
    "reply_content" : ""
}
```

**返回示例**
```
{
   "code": int,         1200 成功 1403 参数错误     2003 检测到敏感词汇
   "description": string,
   "data": "SUCCESS"
}

```
**返回参数说明**
>  无
---

#### 修改关键字
	
**请求地址**
>PUT /keywords
	
**鉴权方式**
> token 鉴权
	
**请求参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id | string | Y | 关键字id
group_codes | list-string | Y | 关键字对应的group_code,多个用 ,隔开
keywords | list-string | Y | 关键字，多个用,隔开
reply_content | string | Y | 触发关键字回复内容

**请求示例**
```
{
    "id": "",
    "group_codes":["",""],
    "keywords": ["", ""],
    "reply_content" : ""
}
```

**返回示例**
```
{
    "code": int,         1200 成功 1403 参数错误     2003 检测到敏感词汇
    "description": string,
    "data": "SUCCESS"
}

```
**返回参数说明**
>  无
---

#### 删除关键字
	
**请求地址**
>DELETE /keywords

**鉴权方式**
> token 鉴权
	
**请求参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id | string | Y | 关键字id

**请求示例**
```
{
    "id":"1bf068bd-f8bd-42d5-9190-054d1c754f50"
}
```

**返回示例**
```
{
    "code": int,         1200 成功 1403 参数错误 
    "description": string,
    "data": "SUCCESS",
}

```
**返回参数说明**
>  无
---


#### 查询关键字列表
	
**请求地址**
>GET /keywords

**鉴权方式**
> token 鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
    "code": "100",
    "description": "",
    "data":[
            {
               "batch_id": "1bf068bd-f8bd-42d5-9190-054d1c754f50", 
               "keywords": ["嘻嘻"],
               "bind_group_counts": 1,
               "reply_content": "呵呵",
               "trigger_times": 0,
               "group_codes": [
                "88A4179651620A56FAF36E748535Agg"
               ]
            },
           ],
    "page_info": {}
}
```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
batch_id | string | Y | 关键字id
keywords | list-string | Y | 关键字，多个用,隔开
bind_group_counts | int | Y | 关键字对应的群数
group_codes | list-string | Y | 关键字对应的group_code
reply_content | string | Y | 触发关键字回复内容
trigger_times| int | Y | 关键字触发次数
---

#### 关键字详情
	
**请求地址**
>GET /keywords/:id

**鉴权方式**
> token 鉴权
	
**请求参数说明** 
> 无

**返回示例**
```
{
    "code": "100",
    "description": "",
    "data":{
            "batch_id": "1bf068bd-f8bd-42d5-9190-054d1c754f50", 
            "keywords": ["嘻嘻"],
            "bind_group_counts": 1,
            "reply_content": "呵呵",
            "trigger_times": 0,
            "group_codes": [
                "88A4179651620A56FAF36E748535Agg"
               ]
            }
}
```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
batch_id | string | Y | 关键字id
keywords | list-string | Y | 关键字，多个用,隔开
bind_group_counts | int | Y | 关键字对应的群数
group_codes | list-string | Y | 关键字对应的group_code
reply_content | string | Y | 触发关键字回复内容
trigger_times| int | Y | 关键字触发次数
---


#### 获取@消息通知开关
	
**请求地址**
>GET  /alt/switch

**鉴权方式**
> token 鉴权

**请求参数说明**
>  无
	
**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": 1       // 0 关闭  1 开启
}
```

**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data |int | Y | 0 关闭  1 开启

---

#### 设置@消息通知开关
	
**请求地址**
>PUT  /alt/switch

**鉴权方式**
> token 鉴权
	
**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
alt_switch | int | Y | 0 关闭通知，1 开启通知

**请求示例**
```
{
    "alt_switch":1
}
```

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": 1       // 0 关闭  1 开启
}
```
---

#### @消息列表
	
**请求地址**
>GET  /alt_msg?current_page= &page_size=

**鉴权方式**
> token 鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page| int | N | 获取第几页数据
page_size | int | N |   每页大小
	
**返回示例**
```
{
  	"code":int,        //1200：正常
  	"data": [
		{
  			msg_id:消息id,
  			group_name:群名,
  			msg_content:消息内容,
  			group_id,
                        status  0:未读，1:已读
		}
  	        ],
  	"description":"描述",
	page_info": {
        "current_page": 0,
        "page_size": 10,
        "total_page": 1,
        "total_records": 3
    }
  }

```
**返回参数说明** 
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
msg_id |string| Y | 消息id
group_name |string| Y | 群名
msg_content |string| Y | 消息内容
group_id |string| Y | 群id
status |int| Y | 0:未读，1:已读
---

#### @消息上下文
	
**请求地址**
>GET  /groups/:group_id/msg/:msg_id/context

**鉴权方式**
> token 鉴权

**请求参数说明** 
> 无
	
**返回示例**
```
{
 	"code":int,        //1200：正常 1404：群不存在
 	"data": [
   		{
   		head_url:头像,
   		nickname:昵称,
   		content:{
                          url,
                          desc,
                          type,
                          title,
                          content,
                          voice_time
                       },
   		send_date:发送时间,
   		mem_code,
   		group_code
   		}
 	 		 ],
 	"description":"描述",
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
head_url |string| Y | 头像
nickname |string| Y | 昵称
content |json| Y | 消息内容
send_date |string| Y | 发送时间
group_code |string| Y | 群code
mem_code |string| Y | 用户code
---

#### 回复@消息
	
**请求地址**
>POST /alt_msg/reply

**鉴权方式**
> token 鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
group_code| string | Y | 群code
mem_code | string  | Y | 用户code
content  | string  | Y | 回复内容 
type     | int     | Y | 消息类型 3文本类型
	
**返回示例**
```
{
	"code":int,        //1200：正常  1404:机器人未找到
  	"data": None,
  	"description":"描述",
	"page_info":{}
}
```
**返回参数说明**
>  无
---

#### 用户已分配的机器人列表
	
**请求地址**
>GET  /user/robots

**鉴权方式**
> token 鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
	"code":int,        //1200：正常 
  	"data": [
		{
  			id:""       // 机器人id,
  			name:"",    // 机器人名称,
  			wechat_no:  // 微信号
		}
  			]
  	"description":"描述"
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id |string| Y | 机器人 id
name |string| Y | 机器人名字
wechat_no |json| Y | 机器人微信号

---

#### 获取问题列表
	
**请求地址**
>GET admin/problems

**是否鉴权**
>  非鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
	"code":int,        //1200：正常 
  	"data":[
		   {
			  id:"",     // 问题id,
			  title:"",  // 标题名称,
			  seq_no:"", // 排序,
		  	  type:""    // 类型
		    }
  			  ]
  	"description":"描述",
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id |string| Y |问题分类 id
title |string| Y | 标题名称
seq_no |json| Y | 排序号
type |json| Y | 类型
---

#### 反馈问题
	
**请求地址**
>POST /user/problem

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
problem_catgory| string | Y | 问题类别id
robot_id | string  | Y | robot_id
group_name  | string  | Y | 群名字
description     | string     | Y | 描述

**请求示例**
```
{
    "problem_catgory":"",
    "robot_id":"",
    "group_name":"",
    "description":""
}
```

**返回示例**
```
{
	"code":int,        //1200：正常 
  	"data": [
		   {
			  id:问题id,
			  title:标题名称,
			  seq_no:排序,
		  	  type:类型
		    }
  			  ]
  	"description":"描述",
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id |string| Y |问题分类 id
title |string| Y | 标题名称
seq_no |json| Y | 排序号
type |json| Y | 类型

---

#### 用户是否封号
	
**请求地址**
>GET /users/block_verify

**是否鉴权**
> token鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
	"code":int,       // 1200：正常
  	"data":boolean,	  // True：封号,False:正常
  	"description":""
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data |boolean| Y |True：封号,False:正常

---

#### 获取用户user_id
	
**请求地址**
>GET  GET /user

**是否鉴权**
> token鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": ""     // 用户user_id
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data |string| Y |用户user_id
---

#### 用户是否注册
	
**请求地址**
>GET  /users/{union_id/registered

**是否鉴权**
> 非鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": true   // True：注册,False:没注册
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data |boolean| Y |True：注册,False:没注册
---

#### 补全用户信息

**请求地址**
>PUT /user/:user_id

**是否鉴权**
> 非鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
union_id | string | Y | 用户union_id
head_url | string | Y | 头像地址
nick_name| string | Y | 昵称
appid    | string | Y | 用户appid
open_id  | string | Y | 用户open_id

**请求示例**
```
{
    "union_id":"",
    "head_url":"",
    "nick_name":"",
    "appid":"",
    "open_id":""
}
```

**返回示例**
```
{
	"code":int,        //1200：正常
  	"data": {
		    red_packed:float
		    }
  	"description":"描述"
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
red_packed|float| Y |红包金额
---

#### 补全用户手机号

**请求地址**
>PUT  /user/phone

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
phone | string | Y | 用户手机号
code  | string | Y | 验证码

**请求示例**
```
{
    "phone":"",
    "code":""
}
```
**返回示例**
```
{
	"code":int,  //1200：正常 2301:验证码错误 2302:验证码过期
  	"data": None
  	"description":"描述"
}
```
**返回参数说明**
>  无
---

#### 补全身份证信息

**请求地址**
>PUT /user/idcard

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id_number | string | Y | 身份证号码
name      | string | Y | 姓名

**请求示例**
```
{
    "id_number":"",
    "name":""
}
```
**返回示例**
```
{
	"code":int,  //1200：正常 2301:验证码错误 2302:验证码过期
  	"data": None
  	"description":"描述"
}
```
**返回参数说明**
>  无
---

#### 设置投放开关

**请求地址**
>PUT /launch/switch

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
code | string | Y |  群code
rcv_task_flag| int | Y | 开关状态 0关闭 1 开启

**请求示例**
```
{
    "code":"",
    "rcv_task_flag":1
}
```

**返回示例**
```
{
	"code":int,        //1200：成功 1101： 失败
  	"description":"描述",
        "data":0 关闭，1 开启
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
data|int| Y |投放开关状态 0 关闭，1 开启
---

#### 投放历史

**请求地址**
>GET /launch/switch?current_page= &page_size=

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page| int | Y | 获取第几页数据
page_size | int | Y |   每页大小


**返回示例**
```
{
	"code": 1200,
	"description": "",
	"data": [{
		"task_id": "",
		"send_date": "",
		"group_count": "",
		"send_flag": 1
	},
			],
	"page_info": {
		"current_page": 0,
		"page_size": 20,
		"total_page": 1,
		"total_records": 7
	}
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
task_id|int| Y |投放任务id
send_date|int| Y |投放时间
group_count|int| Y |投放的群数
send_flag|int| Y |发送状态 0 未发送 1 已发送
---

#### 投放历史详情

**请求地址**
>GET launch/history/detail

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
task_id| sring | Y | 投放id


**返回示例**
```
{
	"code": 1200,
	"description": "",
	"data": {
		"groups": ["mi",],
		"materials": [{
			"url": null,
			"type": 1,
			"title": null,
			"content": "",
			"filePath": null
		},
					 ],
		"send_date": ""
	}
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
groups|list-string| Y |投放的群id 列表
send_date|int| Y |投放时间
materials|int| Y |投放的内容

---

#### 分配机器人

**请求地址**
>POST /robot/distribution

**是否鉴权**
> 非鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
open_id| sring | Y | 用户open_id
union_id| sring | Y | 用户union_id
sharing_user_id| sring | Y | 分享用户user_id
channel| sring | Y | 用户渠道

**请求示例**
```
{
    "open_id":"",
    "union_id":"",
    "sharing_user_id": "",
    "channel":""
 }
```

**返回示例**
```
{
    "code":int,        //1200：成功 1600：机器人未找到
    "description":"描述",
    "data": {
        "head_url": string,  // 头像
        "qr_code": string,   // 二维码
        "wechat_no": string, // 微信号
        "name": string      // 微信昵称
    }
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
head_url| sring | Y | 分配机器人的头像
qr_code| sring | Y | 分配机器人的二维码
wechat_no| sring | Y | 分配机器人的微信号
name| sring | Y | 分配机器人的名字
---

#### 用户收益

**请求地址**
>GET /profit

**是否鉴权**
> token鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": {
        "summary": {
            "amount": "20.14",           // 当前余额
            "balance": "21.15",          // 累计收益
            "yesterday_balance": "1.33"  // 昨日收益
        }
    }
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
amount| sring | Y | 当前余额
balance| sring | Y | 累计收益
yesterday_balance| sring | Y | 昨日收益
---

#### 每日收益明细

**请求地址**
>GET /profit/slip

**是否鉴权**
> token鉴权

**请求参数说明** 
> 无

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": [
        {
            "day": "2019-01-17",
            "balance_detail": "1.33",  // 当日总计
            "detail": [
                {
                    "balance": "0.60", // 收益金额
                    "slip_type": 0     // 收益类型  0:'拉群', 1:'资讯点击', 2:'徒弟徒孙',3:'领养费用',4:'其他'

                },
           
            ]
        }]
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
day| sring | Y | 日期
balance_detail| sring | Y | 当日总计
balance| sring | Y | 该类型的收益金额
slip_type| sring | Y | 收益类型 0:'拉群', 1:'资讯点击', 2:'徒弟徒孙',3:'领养费用',4:'其他'
---

#### 提现接口

**请求地址**
>GET /withdraw

**是否鉴权**
> token鉴权

**返回示例**
```
{
    "code": 1200,
    "description": "",
    "data": {
        "is_withdrawed": true,  // True可提现一元、False不可提现一元
        "id": "",             // 账户id
        "user_id": "",         // 用户id
        "balance_amount": "20.14",  // 可提现金额
        "withdrawing_amount": "0.00"// 提现中的金额
    }
}
```
**返回参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
is_withdrawed| sring | Y | 是否已经提现过
user_id| sring | Y | 用户id
balance_amount| sring | Y | 可提现金额
withdrawing_amount| sring | Y | 提现中的金额

---

#### 确认提现接口

**请求地址**
>POST /withdraw

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
balance| sring | Y | 提现金额

**请求示例**
```
{
    "balance":""
}
```

**返回示例**
```
  {
      "code": int,   // 1200 1200、2001、2002、1200、1403
      "description": string,
      "data": None
  }

```
**返回参数说明**
>  无
---

#### 进入群发消息补全页面

**请求地址**
>GET /tasks/:task_id

**是否鉴权**
> token鉴权

**请求参数说明**
>  无

**返回示例**
```
  {
      "code": int,   // 1200 1200、2001、2002、1200、1403
      "description": string,
      "data": None
  }

```

**返回参数说明**
>  无
---

#### 更新群发消息

**请求地址**
>PUT /tasks/:task_id

**是否鉴权**
> token鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
message| json | Y | 消息内容
group_ids| list-string | Y | 群ids, 多个用,分隔
send_date| string | Y | YYYY-MM-D

message 消息内容参数

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
type| int | Y | 消息类型
content| string | Y | 内容
title| string | Y | 标题
desc| string | Y | 描述
url| string | Y | 链接

**请求示例**
```
{
    "message":{"type":"","content":"","title":"", "desc":"", "url":""},
    "group_ids":["",""],
    "send_date":""
}
```

**返回示例**
```
  {
      "code": int,                    // 1200 成功 2003 检测到敏感词汇
      "description": string,
      "page_info": {}
      "data": None
  }
```
**返回参数说明**
>  无
---

#### 群发消息列表页

**请求地址**
>GET /tasks/messages?direction=

**是否鉴权**
> 非鉴权

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
direction| sring | Y | up 未来一周 down 过去一周


**返回示例**
```
  {
      "code": int,   // 1200 1200、2001、2002、1200、1403
      "description": string,
      "data": None
  }

```
**返回参数说明**
>  无

---

#### 群发消息详情

**请求地址**
>GET /tasks/:task_id/message

**是否鉴权**
> token鉴权

**请求参数说明** 
> 无

**返回示例**
```
  {
      "code": int,
      "description": string,
      "data": {
          "groups_info": [{
              "id": string            // 群ID
              "name": string          // 群昵称
          }],
          "content": [{
              "type": int            // 消息类型
              "content": string      // 内容
              "title": string        // 标题
              "desc": string         // 描述
              "url": string          // 链接
          }],
          "send_date": string        // 发送时间
      }
  }
```

**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id| sring | Y | 群ID
name| sring | Y | 群昵称
type| int | Y | 消息类型
content| sring | Y | 内容
title| sring | Y | 标题
desc| sring | Y | 描述
url| sring | Y | 链接
send_date| sring | Y | 发送时间
---

#### 群发消息撤回

**请求地址**
>DEL /tasks/:task_id

**是否鉴权**
> token鉴权

**请求参数说明** 
>  无

**返回示例**
```
  {
      "code": int,                    // 1200
      "description": string,
      "data": None
  }

```
**返回参数说明** 
>  无
---

#### 获取当前token的用户ID

**请求地址**
>GET /auth/me

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
Authorization| sring | Y | Bearer <access_token>

**返回示例**
```
{
    "me": {
        "user_id": ""
    },
    "code": 1200,
    "msg": ""
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
user_id| sring | Y | 用户user_id
---



### web后台接口

#### 提现列表

**请求地址**
>POST /admin/withdraw?current_page=0&page_size=100 

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page| int | Y | 页数
page_size| int | Y | 每页大小
phone| string | N | 手机号码
amount_begin| int | N | 起始金额
amount_end| int | N | 结束金额
withdraw_date_begin| string | N | 提现开始日期
withdraw_date_end| string | N | 提现结束日期
paid_date_begin| string | N | 打款开始日期
paid_date_end| string | N | 打款结束日期
status| int | N | 打款状态
sort| json | N | 排序方式

sort参数说明

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
sort_key| int | N | 排序依据 amount 金额 create_date 提现日期 paid_date 打款日期
value| int | N | 排序方式 asc  升序 desc 降序

**返回示例**
```
{
    "code":1200,
    "description":"",
    "data":[
        {
            "id":"15e1c365-5c8d-488f-8238-f7ab4be89391",
            "phone":"13528779113",
            "amount":"1892.46",
            "reason":null,
            "create_date":"2018-05-25 16:58:20",
            "paid_date":"2018-05-28 16:34:38",
            "status":3
        }
    ],
    "page_info":{
        "current_page":0,
        "page_size":100,
        "total_page":1400,
        "total_records":139930
    }
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
id| sring | Y | 用户user_id
phone| sring | Y | 电话号码
amount| sring | Y | 提现金额
reason| sring | Y | 打款失败原因
create_date| sring | Y | 创建时间
paid_date| sring | Y | 支付时间
status| int | Y | 用户user_id

---

#### 后台问题反馈列表

**请求地址**
>POST /admin/problem/feedback?current_page=0&page_size=100

**请求参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
current_page| int | Y | 页数
page_size| int | Y | 每页大小
phone| string | N | 手机号码
problem_id| int | N | 问题分类id
robot_code| int | N | 机器人code
group_name| string | N | 群名
commit_date_begin| string | N | 反馈提交开始日期
commit_date_end| string | N | 反馈提交结束日期


**返回示例**
```
{
    "code":1200,
    "description":"",
    "data":[
        {
            "phone":"18112333627",
            "nickname":"霍霍💋",
            "title":"提现超过3个工作日未到帐",
            "code":null,
            "name":null,
            "wechat_no":null,
            "group_name":null,
            "description":null,
            "create_date":"2019-01-24 08:14:08"
        }
    ],
    "page_info":{
        "current_page":0,
        "page_size":100,
        "total_page":32,
        "total_records":3146
    }
}
```
**返回参数说明** 

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
phone| sring | Y | 电话号码
nickname| sring | Y | 用户昵称
title| sring | Y | 反馈类型
code| sring | Y | 机器人code
name| sring | Y | 机器人昵称
wechat_no| int | Y | 微信号
group_name| int | Y | 群名字
description| int | Y | 描述
create_date| int | Y | 反馈时间

### 外部接口

#### 阿里云客服回调

**请求地址**
>POST /aliyun/callback?timestamp=1487230487910&digest=xxxxxx
	
**请求参数说明**

参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
userId | string | Y | 实际为系统内部user_code
msgType | string | Y | 消息类型
content | string | Y | 消息
timestamp | int | Y | 时间戳，用作校验
digest | int | Y | 摘要，用作校验

**请求示例**
```
{
   "userId": "12345",
　　"msgType": "text",
　　"content": "hello world",
　　"timestamp": 1487230487910,
　　"serverName": "客服007"
}
```
	
**返回示例**
	
```
{
	"code": 1200,
	"description": "",
	"data": null
}
	
```
**返回参数说明** 
> 无
---

#### 群星级评定
	
**请求地址**
>POST /groups/star

**是否鉴权**
> 非鉴权
	
**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
command | string | Y | 数据类型
groupId | string | Y | 对应系统内部group_code
state | int | Y | 状态 0-undefined，1-initial，2-upgraded，3-degraded，4-confirmed，5-manual set，6-timeout set，10-quit
star | int | Y | 群所对应的星级 1、2、3、4、5

**请求示例**
	
```
{
    "command":"update_group_star",
    "data":[{
        "groupId": "",
        "state": 1, //评星状态，0-undefined, 1-init 2-upgrade
        "star": 1
    }]
}
```
	
**返回示例**
	
```
{
	"code": 1200,
	"description": "",
	"data": null,
}
	
```
**返回参数说明**
> 无
---

#### 群投放

**请求地址**
>POST /task/receive
	
**请求参数说明**
	
参数 | 类型 | 是否必须 | 说明
:---:|:---:|:---:|:---:
taskId | string | Y | 对应投放系统任务批次主键
groupIds | List | Y | 需要投放的群列表
content | object | Y | 投放详细内容

**请求示例**
	
```
 {
    "taskId": string, //  任务id，用于追踪任务完成情况
    "groupIds": ["", ""],
    "content": {
        "items": [
            {
                "type": number // 内容类型，1-文字；2-图片；3-链接；4-小程序
                "title": string // 标题，仅供链接、小程序使用，其他为空
                "content": string // 内容，供文字、链接、小程序使用，其他为空(小程序为小程序的图片路径)
                "filePath": string // 图片、视频、音频存放路径
                "url": string // 链接为落地页，小程序为weburl
            }
        ]
    }
 }
```
	
**返回示例**
	
```
{
	"code": 1200,
	"description": "",
	"data": null,
	"page_info": {}
}
	
```
**返回参数说明**
> 无

---

#### 错误码对照表
code | 错误说明 |
:---:|:---:|
1200 | 正常 
1401 | 鉴权失败 
1403 | 请求参数错误
2003 | 用户触发敏感词