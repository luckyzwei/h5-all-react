// import {Base64} from 'js-base64'

export const sendEvent = (key, value) => {
    var event = new Event(key);
    event.newValue = value;
    window.dispatchEvent(event);
}
//sendEvent("messages", {msg: "创建群发成功", status: 200})
export const formatDate = (strTime, type) => {
    var date = new Date(strTime)
    var year = date.getFullYear()
    var month = ((date.getMonth() + 1) < 10) ? '0' + (date.getMonth() + 1) : (date.getMonth() + 1)
    var day = (date.getDate() < 10) ? '0' + date.getDate() : date.getDate()
    var hours = (date.getHours() < 10) ? '0' + date.getHours() : date.getHours()
    var minutes = (date.getMinutes() < 10) ? '0' + date.getMinutes() : date.getMinutes()
    var seconds = (date.getSeconds() < 10) ? '0' + date.getSeconds() : date.getSeconds()
    switch (type) {
        case 'yy/mm/dd':
            return String(year).slice(2) + "/" + month + "/" + day
        case 'yyyy/mm/dd':
            return year + "/" + month + "/" + day
        case 'yyyy/mm/dd hh:mm':
            return year + "/" + month + "/" + day + " " + hours + ":" + minutes
        default:
            return year + "/" + month + "/" + day + " " + hours + ":" + minutes + ":" + seconds
    }
}

export const format_date = (time, type) => {
    switch (type) {
        case 'YYYY/MM/DD':
            return time.slice(0, 10).replace(/-/g, '/');
        case 'MM/DD':
            return time.slice(5, 10).replace('-', '/');
        case 'MM/DD HH:MM':
            return time.slice(5, 16).replace('-', '/');
        case 'YYYY-MM-DD HH:MM':
            return time.slice(0, 16).replace(/\//g, '-');// 2018/11/28 16:30->2018-11-21 12:00:00"
        default:
            return;
    }
}

// fetch a single param from url
export const getQueryString = (name) => {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null)
        return (r[2]);
    return null;
}
//验证长度 32个字节 16个汉字
export const TextCountRange = (str) => {
    let countf = str.replace(/[^\\x00-\\xff]/g, "oo").length / 2;
    return countf
}

//截取字符串字节
export const strLenIndex = (str, length) => {
    var count = 0
    var j = 0;
    for (var i = 0, len = str.length; i < len; i++) {
        j = i
        count += str.charCodeAt(i) < 256 ? 1 : 2;
        if (count > length) {
            return j
        }
    }
}
// fetch all param from url
export const getSearch = () => {
    let search = window.location.search.slice(1).split('&')
    let params = {}
    search.forEach(item => {
        let param = item.split('=')
        params[param[0]] = param[1]
    })
    return params
}

export const phoneVerify = (str) => {
    let myreg = /^1[3-9]{1}\d{9}$/;
    if (myreg.test(str)) {
        return true
    }
}

export const codeVerify = (str) => {
    let myreg = /^\d{6}$/;
    if (myreg.test(str)) {
        return true
    }
}

export const saveCookie = (name, data, time) => {
    let exp = new Date();
    if(time){
        exp.setTime(exp.getTime() + 90 * 24 * 3600 * 1000)
    }else{
        exp.setTime(exp.getTime() + time)
    }
    document.cookie = name + "=" + escape(data) + ";expires=" + exp.toGMTString() + ';path=/';
}

export const getCookie = (name, time) => {
    var aCookie = document.cookie.split("; ");
    for (var i = 0; i < aCookie.length; i++) {
        var aCrumb = aCookie[i].split("=");
        if (name === aCrumb[0])
            return unescape(aCrumb[1])
    }
    return null;
}

export const deleteCookie = (name) => {
    var exp = new Date();
    exp.setTime(exp.getTime() - 10);
    var cval = getCookie(name);
    if (cval != null)
        document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString() + ';path=/';
}
