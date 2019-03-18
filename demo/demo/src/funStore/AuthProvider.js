import {login_get_token} from '../funStore/CommonPort'
import {saveCookie,getCookie,deleteCookie} from './CommonFun'

class AuthProvider {
    onLogin(unionid) {
        const self = this
        return login_get_token({union_id:unionid}).then(res => {
            const data = res
            self.saveTokens(data.access_token, data.refresh_token)
            return data
        }).catch((reject) => {
            return 'error'
        })
    }


    onRefreshToken() {
        const unionid = getCookie('union_id')
        deleteCookie('access_token')
        return this.onLogin(unionid)
    }

    saveTokens(access_token, refresh_token) {
        saveCookie('access_token',access_token, 1*3600*1000)
    }
}

export default new AuthProvider()
