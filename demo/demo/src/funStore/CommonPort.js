import {API_URL} from '../constants/Api'
import AxiosCore from './AxiosCore'

/** 公众号授权 (微信授权) 获取用户信息*/
export const we_chat_login = (urlComple) => {
    return AxiosCore.request({url: API_URL.weChat + urlComple, method: 'GET', isAuth: false})
}

/** 获取token */
export const login_get_token = (parmas) => {
    return AxiosCore.request({url: API_URL.auth, method: 'POST', data: parmas, isAuth: false})
}

/** 获取unionid之后判断用户是否注册 */
export const is_registered = (unionid) => {
    return AxiosCore.request({url: API_URL.isRegistered + unionid + '/registered', method: 'GET', isAuth: false})
}

/** 补全信息 */
export const fill_userInfo = (parmas) => {
    return AxiosCore.request({url: API_URL.fillUser, method: 'post', data: parmas, isAuth: false})
}
/** 机器人分配（添加机器人好友）* */
export const get_robot = (unionId) => {
    return AxiosCore.request({url: API_URL.getRobot + unionId, method: 'get', isAuth: false})
}
/**群列表 */
export const group_list = (unionId) => {
    return AxiosCore.request({url: API_URL.groupList + unionId + '/groups', method: 'GET', isAuth: false})
}

/**标签 */
export const get_labels = () => {
    return AxiosCore.request({url: API_URL.labels, method: 'GET', isAuth: false})
}

/**投放内容*/
export const get_ads = (group_id) => {
    return AxiosCore.request({url: API_URL.ads + group_id, method: 'GET', isAuth: false})
}
/**设置投放内容*/
export const set_ads = (parmas) => {
    return AxiosCore.request({url: API_URL.setAds, data: parmas, method: 'post', isAuth: false})
}
/**获取机器人群内昵称*/
export const get_robot_name = (group_id) => {
    return AxiosCore.request({url: API_URL.getRobotName + group_id, method: 'get', isAuth: false})
}

/**获取机器人群内昵称*/
export const change_robot_name = (parmas) => {
    return AxiosCore.request({url: API_URL.changeRobotkName, data: parmas, method: 'post', isAuth: false})
}


























