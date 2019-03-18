// 参数： eventName [, options]
// eventName
// options

var host = '',
    site = '',
    uuid = '';

window.G_SDK = {
    SDK: function (env, sites) {
        host = env.toLowerCase() === 'prd' ? 'https://gpetprd.gemii.cc' : 'https://gpetdev.gemii.cc';
        site = sites
        uuid = getUUID()
    },
    loading: function () {
        // loading
        var ar = arguments
        var __pathname = location.href
        var url = `${host}/page/access?_s=${site}&_p=${encodeURIComponent(__pathname)}&_u=${uuid}&_e=__LOADING__`
        for (var i = 0; i < ar.length; i++) {
            url = url + '&_a' + (i + 1) + '=' + ar[i]
        }
        __ajax({
            url: url,
            type: 'get',
            data: null
        })
    },
    loaded: function () {
        // loaded
        var ar = arguments
        var __pathname = location.href
        var url = `${host}/page/access?_s=${site}&_p=${encodeURIComponent(__pathname)}&_u=${uuid}&_e=__LOADED__`
        for (var i = 0; i < ar.length; i++) {
            url = url + '&_a' + (i + 1) + '=' + ar[i]
        }
        __ajax({
            url: url,
            type: 'get',
            data: null
        })
    },
    push: function () {
        var ar = arguments
        var __pathname = location.href
        var __event = ar[0]
        var url = `${host}/page/access?_s=${site}&_p=${encodeURIComponent(__pathname)}&_u=${uuid}&_e=${__event}`
        if (ar.length > 1) {
            for (var i = 1; i < ar.length; i++) {
                url = `${url}&_a${i}=${ar[i]}`
            }
        }
        __ajax({
            url: url,
            type: 'get',
            data: null
        })
    }

}

// ajax请求
// url 链接
// type 请求类型
// data 请求数据
// successCall 成功回调
// errCall 失败回调
function __ajax(conf) {
    var {url, type, data, successCall, errCall} = conf
    var xhr = new XMLHttpRequest();
    xhr.open(type, url, true);
    // xhr.withCredentials = true;
    if (typeof data === 'object') {
        xhr.setRequestHeader('Content-Type', 'application/json')
        data = JSON.stringify(data)
    } else {
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
    }
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status >= 200 && xhr.status < 300 || xhr.status === 304) {
                successCall && successCall(xhr.responseText)
            } else {
                errCall && errCall(xhr.responseText)
            }
        }
    }
    xhr.send(data);
}

function __setCookie(name, value) {
    var days = 1
    var exp = new Date()
    exp.setTime(exp.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = name + "=" + escape(value) + ";path=/;expires=" + exp.toGMTString();
}

// 获取cookie
function __getCookie(name) {
    var arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
    return unescape(arr[2]);
}

// 生成唯一标识
function __uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function getUUID() {
    var uuid
    try {
        uuid = __getCookie('uuid_')
    } catch (error) {
        uuid = __uuid()
        __setCookie('uuid_', uuid)
    }
    return uuid
}
