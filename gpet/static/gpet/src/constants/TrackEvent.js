import {getCookie} from '../funStore/CommonFun'
export const tongji = function(){
    const unionId = getCookie('union_id')
    let ars = Array.from(arguments)
    let eventname = ars[0]
    let others = ars.slice(1)
    window.G_SDK.push('gpet_'+eventname,unionId,...others)
}



