export const API_URL = {
    weChat:'temp/wechat/h5/user_info?',             //公众号授权 unionId opendId等 `${API_PATH}/wechat/user_info?app_id=${appid}&code=${code}`
    getRobot: '/temp/wechat/distribute?union_id=',        //机器人分配
    isRegistered: '/temp/users/',                 // 获取unionid之后判断用户是否注册
    fillUser:'/temp/user/complete',//补充用户信息
    labels:'/temp/labels', //获取标签列表
    ads: '/temp/ads?id=',//获取投放内容
    setAds: 'temp/ads',//设置头发预览
    getRobotName:'/temp/group/robot/nickname?group_id=',//获取机器人群内昵称
    changeRobotkName:'/temp/group/robot_name',//修改群内机器人昵称
    groupList:'/temp/user/',//群列表
    auth:'/auth',//获取token
}
