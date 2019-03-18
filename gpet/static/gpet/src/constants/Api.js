export const API_URL = {

    weChat:'wechat/user_info?',             //公众号授权 unionId opendId等 `${API_PATH}/wechat/user_info?app_id=${appid}&code=${code}`
    wechatTicket:'/wechat/js/ticket',       //获取微信分享信息 appid，timestamp等 `${API_PATH}/wechat/js/ticket?app_id=${APP_ID}&url=${url}`

    auth:'/auth',                           //获取token
    accessPage:'/page/access',              //统计用户是否进入过任意页面

    appStatus: '/app/status',               //系统状态判断 status 1代表服务正常 2代表服务维护
    getVerifyCode:'/sms/code/delivery?phone=',//获取验证码

    isRegistered: '/users',                 // 获取unionid之后判断用户是否注册
    ownerIsGroup: '/owner/group/verify',   //是否有群主群
    ownerGroupList: '/owner/groups',        // 群主群列表 current_page='+current_page+'&page_size='+page_size
    getRobot: '/robot/distribution',        //机器人分配
    importRobot:'/robot/show',              //导入群

    isReceivedRed:'/received/redpacket', //判断是否有领取过红包
    receivedRed:'/receive/redpacket',    //领取红包

    groupList:'/groups?',//群列表

    getUserId: '/user',                      // 获取当前用户的UserId
    fillIdCard:'/user/idcard',              //补全身份证信息
    fillPhone:'/user/phone',                //补全手机号

    checkAuth: '/users/block_verify',        // 检查账号(用户)是否封掉
    checkAccout: '',                         //登录成功之后检查机器人是否封号
    refreshUserInfo: '/user/refresh/',       //刷新用户信息
    homeGroupCount: '/user/groups/disciples',     // 获取群宠概要

    keywords: '/keywords',                  //关键词

    poster:'/user/',//海报

    discipleList: '/user/apprentice?',      //获取徒弟徒孙列表
    discipleWake: '/apprentice/awakening',   //唤醒徒弟

    pullbackPet:'/pullback/',//拉回群宠

    getProfit:'/profit',                    //获取收益详情
    getProfitList:'/profit/slip',           //获取收益明细
    withdraw:'/withdraw',                   //提现

    altmsg:'/alt_msg?',                     //获取@我信息列表
    altswitch:'/alt/switch',                //是否有开启@功能 0关闭，1开启
    altmsgContent:'/groups/',               //获取alt上下文 /groups/${message.group_id}/msg/${message.msg_id}/context
    altReply:'/alt_msg/reply',              //回复@消息

    groupStatistics:'/groups/statistics?',  //群数据

    welcomeList:'/groups/welcome',        //获取群宠群主群群欢迎语
    saveWelcome:'/groups/',                //保存欢迎语

    createMassMsg:'/tasks/',                        //群发消息
    massMsgList:'/tasks/messages?direction=',       //群发消息list

    problemsBack:'/problems',                       //问题反馈
    pushProblems:'/user/problem',                    //提交问题反馈
    selectPet:'/user/robots',               //选择微小宠

    taskHistory:'/launch/history?',         //文章推送 3天投放数据
    taskDetail:'/launch/history/detail?task_id=',                  //文章详情查看
    taskRange:'/launch/switch',             //文章投放范围
    setMarquee:'/app/marquee',//首页跑马灯状态和内容
}
