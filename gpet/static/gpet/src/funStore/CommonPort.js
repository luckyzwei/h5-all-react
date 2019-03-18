import {API_PATH} from '../constants/OriginName'
import {API_URL} from '../constants/Api'
import AxiosCore from './AxiosCore'

/** 公众号授权 (微信授权) 获取用户信息*/
export const we_chat_login=(urlComple)=>{
    return AxiosCore.request({url: API_URL.weChat+urlComple, method: 'GET', isAuth:false})
}
/**获取微信分享信息*/
export const getWechat=(urlComple)=>{
    return AxiosCore.request({url: API_URL.wechatTicket + urlComple , method: 'GET', isAuth: false})
}

/** 获取token */
export const login_get_token=(parmas)=>{
    return AxiosCore.request({url: API_URL.auth, method: 'POST', data: parmas, isAuth:false})
}

/**获取验证码 **/
export const get_verify_code = (phone) => {
    return AxiosCore.request({url: API_URL.getVerifyCode + phone, method: 'GET', isAuth: true})
}

/** 获取unionid之后判断用户是否注册 */
export const is_registered = (unionid) => {
    return AxiosCore.request({url: API_URL.isRegistered + unionid, method: 'GET', isAuth: false})
}
/** 补全信息 */
export const fill_userInfo = (userId, parmas) => {
    return AxiosCore.request({url: API_URL.getUserId + `/${userId}`, method: 'PUT', data: parmas, isAuth: false})
}
/** 领取红包 */
export const is_received_red=()=>{
    return AxiosCore.request({url:API_URL.isReceivedRed,method:'GET',isAuth: true})
}
export const receive_red_packet=()=>{
    return AxiosCore.request({url:API_URL.receivedRed,method:'GET',isAuth: true})
}
/** 刷新用户信息 */
export const refresh_user_info = (unionId, parmas) => {
    return AxiosCore.request({url: API_URL.refreshUserInfo + unionId, method: 'PUT', data: parmas, isAuth: true})
}
/** 首页中获取群概要 */
export const home_group_count = () => {
    return AxiosCore.request({url: API_URL.homeGroupCount, method: 'GET', isAuth: true})
}
/** 检查账号(用户)是否封掉 */
export const check_auth = () => {
    return AxiosCore.request({url: API_URL.checkAuth, method: 'GET', isAuth: true})
}
/** 登录成功之后检查机器人是否封号 此版本功能不做 */
export const check_pet_Accout = () => {
    return AxiosCore.request({url: API_URL.checkAccout, method: 'GET', isAuth: true})
}

/** 机器人分配（添加机器人好友）* */
export const get_robot = (parmas) => {
    return AxiosCore.request({url: API_URL.getRobot, method: 'post', data: parmas, isAuth: true})
}
/** 拉回群宠 */
export const pullback_petRobot = (groupId) => {
    return AxiosCore.request({url: API_URL.pullbackPet + groupId, method: 'GET', isAuth: true})
}

/** 拉群 导群 */
export const import_robot = (parmas) => {
    return AxiosCore.request({url: API_URL.importRobot, method: 'get', data: parmas, isAuth: true})
}

/** 是否有群主群 */
export const OwnerIsGroup = () => {
    return AxiosCore.request({url: API_URL.ownerIsGroup, method: 'GET', isAuth: true})
}
/** 群主群列表 "data": False 没有群主群，True 有群主群 */
export const OwnerGroupList = (current_page, page_size) => {
    return AxiosCore.request({
        url: API_URL.ownerGroupList + '?current_page=' + current_page + '&page_size=' + page_size,
        method: 'GET',
        isAuth: true
    })
}

/** 关键词 */
export const Keywords = () => {
    return AxiosCore.request({url: API_URL.keywords, method: 'GET', isAuth: true})
}//查询类别
export const Keywords_DELETE = (parmas) => {
    return AxiosCore.request({url: API_URL.keywords, method: 'DELETE', data: parmas, isAuth: true})
}//关键词删除
export const Keywords_data_list = (id) => {
    return AxiosCore.request({url: API_URL.keywords + id, method: 'GET', isAuth: true})
} //获取需编辑的关键词
export const Keywords_EDIT = (parmas, type) => {
    return AxiosCore.request({
        url: API_URL.keywords,
        method: type === 'PUT' ? 'PUT' : 'POST',
        data: parmas,
        isAuth: true
    })

}//编辑新增关键词


/**群列表 */
export const group_list = (urlComple) => {
    return AxiosCore.request({url: API_URL.groupList + urlComple, method: 'GET', isAuth: true})
}
/**修改群昵称 `${API_PATH}/groups/${checkItem.id}/robot_name`*/
export const change_robot_name = (urlComple, parmas) => {
    return AxiosCore.request({url: API_URL.saveWelcome + urlComple, data: parmas, method: 'PUT', isAuth: true})
}

/** 徒弟徒孙 */
export const disciple_list = (urlComple) => {
    return AxiosCore.request({url: API_URL.discipleList + urlComple, method: 'GET', isAuth: true})
}
export const disciple_wake = (parmas) => {
    return AxiosCore.request({url: API_URL.discipleWake, data: parmas, method: 'POST', isAuth: true})
}

/** 收徒;获取当前用户的UserId */
export const get_userId = () => {
    return AxiosCore.request({url: API_URL.getUserId, method: 'GET', isAuth: true})
}
/** 收徒； 获取收徒的海报地址 */
export const get_porterUrl = (user_id) => {
    const url = `${API_PATH}/user/${user_id}/poster`
    return AxiosCore.request({url: url, method: 'GET', isAuth: true})
        .then(res => {
            return url
        })
}

/**@我*/
export const get_altmsg = (urlComple) => {
    return AxiosCore.request({url: API_URL.altmsg+urlComple, method: 'GET', isAuth: true})
}
export const get_altswitch = () => {
    return AxiosCore.request({url: API_URL.altswitch, method: 'GET', isAuth: true})
}
export const chenge_altswitch = (parmas) => {
    return AxiosCore.request({url: API_URL.altswitch, method: 'PUT', data: parmas, isAuth: true})
}
export const get_altmsg_content = (urlComple) => {
    return AxiosCore.request({url: API_URL.altmsgContent + urlComple, method: 'GET', isAuth: true})
}
export const alt_reply = (parmas) => {
    return AxiosCore.request({url: API_URL.altReply, method: 'POST', data: parmas, isAuth: true})
}


/**获取收益详情； 获取收益明细 */
export const get_profit = () => {
    return AxiosCore.request({url: API_URL.getProfit, method: 'GET', isAuth: true})
}
export const get_profit_list = () => {
    return AxiosCore.request({url: API_URL.getProfitList, method: 'GET', isAuth: true})
}
/**提现*/
export const get_withdraw_data = () => {
    return AxiosCore.request({url: API_URL.withdraw, method: 'GET', isAuth: true})
}
export const request_withdraw = (parmas) => {
    return AxiosCore.request({url: API_URL.withdraw, method: 'POST', data: parmas, isAuth: true})
}

/**提现中 补全身份证、手机号*/
export const fill_IdCard = (parmas) => {
    return AxiosCore.request({url: API_URL.fillIdCard, method: 'PUT', data: parmas, isAuth: true})
}
export const fill_Phone = (parmas) => {
    return AxiosCore.request({url: API_URL.fillPhone, method: 'PUT', data: parmas, isAuth: true})
}

/**文章投放范围*/
export const task_range = (parmas) => {
    return AxiosCore.request({url: API_URL.taskRange, method: 'PUT', data: parmas, isAuth: true})
}

/**群数据*/
export const group_statistics = (urlComple) => {
    return AxiosCore.request({url: API_URL.groupStatistics + urlComple, method: 'GET', isAuth: true})
}

/**欢迎语*/
export const get_welcome_list = () => {
    return AxiosCore.request({url: API_URL.welcomeList, method: 'GET', isAuth: true})
}
export const save_welcome = (urlComple, parmas) => {
    return AxiosCore.request({url: API_URL.saveWelcome + urlComple, method: 'POST', data: parmas, isAuth: true})
}

/**群发消息*/
export const get_create_msg_list = (task_id) => {
    return AxiosCore.request({url: API_URL.createMassMsg + task_id, method: 'GET', isAuth: true})
}
export const create_mass_msg = (task_id, parmas) => {
    return AxiosCore.request({url: API_URL.createMassMsg + task_id, method: 'PUT', data: parmas, isAuth: true})
}
export const get_massmsg_content = (urlComple) => {
    return AxiosCore.request({url: API_URL.createMassMsg + urlComple, method: 'GET', isAuth: true})
}
export const get_mass_msg_list = (urlComple) => {
    return AxiosCore.request({url: API_URL.massMsgList + urlComple, method: 'GET', isAuth: true})
}
export const delete_mass_msg = (task_id) => {
    return AxiosCore.request({url: API_URL.createMassMsg + task_id, method: 'DELETE', isAuth: true})
}

/**问题反馈*/
export const problems_back = () => {
    return AxiosCore.request({url: API_URL.problemsBack, method: 'GET', isAuth: true})
}
export const push_problems_back = (parmas) => {
    return AxiosCore.request({url: API_URL.pushProblems, method: 'POST', data: parmas, isAuth: true})
}
export const select_pet = () => {
    return AxiosCore.request({url: API_URL.selectPet, method: 'GET', isAuth: true})
}

/**文章推送*/
export const task_history_list = (urlComple) => {
    return AxiosCore.request({url: API_URL.taskHistory + urlComple, method: 'GET', isAuth: true})
}
export const task_detai = (id) => {
    return AxiosCore.request({url: API_URL.taskDetail + id, method: 'GET', isAuth: true})
}

/**首页跑马灯状态和内容*/
export const set_marquee = (urlComple) => {
    return AxiosCore.request({url: API_URL.setMarquee , method: 'GET', isAuth: false})
}




















