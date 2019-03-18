import { APP_ID } from '../constants/OriginName';
import {we_chat_login} from '../funStore/CommonPort'
import {getQueryString,getCookie,saveCookie} from './CommonFun'
/* global location */
/* eslint no-restricted-globals: ["off", "location"] */
class AccountInfo {
    requestUnionId(){
        // 判断是否获取到unionId，没有则去拿取
        const unionId = getCookie('unionId_demo')
        const openId = getCookie('openId_demo')
        const headUrl = getCookie('headUrl_demo')
        const nickName = getCookie('nickName_demo')
        if(unionId!==null&&unionId!=='undefined'&&unionId!=='null'){
            return new Promise((resolve, reject) => {
                resolve({
                    unionid:unionId,
                    openid: openId,
                    headimgurl: headUrl,
                    nickname: nickName
                })
            })
        }
        const appid= APP_ID
        let code = getQueryString('code')
        if(code===null){
            //静默授权
            location.href = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appid}&redirect_uri=${escape(location.href)}&response_type=code&scope=snsapi_userinfo&connect_redirect=1#wechat_redirect`
        }else {
            //根据code获取用户微信信息 url = `${API_PATH}/wechat/user_info?app_id=${appid}&code=${code}`
            return we_chat_login(`app_id=${appid}&code=${code}`).then(res => {
                if (res.code === 1200) {
                    let resData= res.data
                    saveCookie('unionId_demo',resData.unionid)
                    saveCookie('openId_demo',resData.openid)
                    saveCookie('headUrl_demo',resData.headimgurl)
                    saveCookie('nickName_demo',resData.nickname)
                    return resData
                }
            })
        }
    }
}
export default new AccountInfo()
