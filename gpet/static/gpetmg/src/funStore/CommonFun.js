export const sendEvent = (key, value) => {
    var event = new Event(key);
    event.newValue = value;
    window.dispatchEvent(event);
}
//sendEvent("messages", {msg: "创建群发成功", status: 200})

// fetch a single param from url
export const getQueryString = (name) => {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null)
        return (r[2]);
    return null;
}

export const  phoneVerify=(str)=>{
    let myreg = /^1[3-9]{1}\d{9}$/;
    if(myreg.test(str)){
        return true
    }
}

export const codeVerify=(str)=>{
    let myreg = /^\d{6}$/;
    if(myreg.test(str)){
        return true
    }
}

export const saveCookie=(name,data)=>{
    let exp = new Date();
    exp.setTime(exp.getTime() + 90*24*3600*1000)
    document.cookie = name + "="+ escape (data) + ";expires=" + exp.toGMTString()+';path=/';
}

export const getCookie=(name)=> {
    var aCookie = document.cookie.split("; ");
    for (var i = 0; i < aCookie.length; i++) {
        var aCrumb = aCookie[i].split("=");
        if (name === aCrumb[0])
            return unescape(aCrumb[1]);
    }
    return null;
}

export const deleteCookie=(name)=>{
    var exp = new Date();
    exp.setTime(exp.getTime() - 90*24*3600*1000);
    var cval = getCookie(name);
    if (cval != null)
        document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
}


