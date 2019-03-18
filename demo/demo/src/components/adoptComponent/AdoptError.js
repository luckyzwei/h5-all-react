import React from 'react'
export const Error1 = () => {
    return (
        <div className="error-wrapper">
            <p>今天的免费额度已经领完啦，<br/>明天早点来接我哦~</p>
            <img src={process.env.PUBLIC_URL+"/images/icon/pic_404.png"} alt=""/>
        </div>
    )
}

export const Error2 = () => {
    return (
        <div className="error-wrapper">
            <p>今天的微小宠已全部被领养<br/>新的正在紧急训练中<br/>请明天早点来领养哦</p>
            <img src={process.env.PUBLIC_URL+"/images/icon/pic_404.png"} alt=""/>
        </div>
    )
}


export const Error3 = () => {
    return (
        <div className="error-wrapper">
            <p>主人网络有点差哦！<br/>换个网络试试吧！</p>
            <img className='img404' src={process.env.PUBLIC_URL+"/images/icon/pic_404.png"} alt=""/>
            <div className="refreshBtn" onClick={()=>{window.location.href = window.location.origin+window.location.pathname+'?'+new Date().getTime()}}>刷新</div>
        </div>
    )
}
