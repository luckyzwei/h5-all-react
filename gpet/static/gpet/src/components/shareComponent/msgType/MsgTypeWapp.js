import React from 'react'
import $ from 'jquery'
import {tongji} from '../../../constants/TrackEvent'
import './msgTypeUnit.scss'
const cDataParse = (str) => {
    if(str.includes('CDATA')){
        return str.substr(9,str.length-12)
    }else {
        return str
    }
}

export const Text = (props) => {
    return (
        <div className="bubble">
            <div className="avatar">
                <img src={'/images/icon/xiaoxiong.png'} alt=""/>
            </div>
            <div className="bubbleContent">
                <div className="nickName">小熊</div>
                <div className="bubbleBox textBox">
                    {props.item.content}
                </div>
            </div>
        </div>
    )
}

export const Link = (props) => {
    return (
        <div className="bubble">
            <div className="avatar">
                <img src={'/images/icon/xiaoxiong.png'} alt=""/>
            </div>
            <div className="bubbleContent">
                <div className="nickName">小熊</div>
                <div className="bubbleBox linkBox" onClick={()=>{
                    window.location.href=props.item.url;
                    tongji('task_h5TiaoZhuan');
                }}>
                    <div className="linkTitle textHide">{props.item.title}</div>
                    <div style={{display:'flex'}}>
                        <div className="linkContent textHide-2">{props.item.content}</div>
                        <img src={props.item.filePath} alt="" className="linkPic"/>
                    </div>
                </div>
            </div>
        </div>
    )
}

//返回xml数据
export const Wxapp = (props) => {
    return (
        <div className="bubble">
            <div className="avatar">
                <img src={'/images/icon/xiaoxiong.png'} alt=""/>
            </div>
            <div className="bubbleContent">
                <div className="nickName">小熊</div>
                <div className="bubbleBox wxappBox">
                    <div className="wxappTitle">
                        <img src={$(props.item.filePath).find('weappiconurl') ? $(props.item.filePath).find('weappiconurl').text(): ''} alt="" />
                        <span>{$(props.item.filePath).find('sourcedisplayname').text()}</span>

                    </div>
                    <div className="wxContent textHide">{cDataParse($(props.item.filePath).find('title').eq(0).text())}</div>
                    <img className="wxImg" src={props.item.content} alt=""/>
                    <div className="wxappFooter">
                        <img className="wxappLogo" src={"/images/icon/weapp_logo.png"} alt=""/>
                        <span>小程序</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export const Pic = (props) => {
    return (
        <div className="bubble">
            <div className="avatar">
                <img src={'/images/icon/xiaoxiong.png'} alt=""/>
            </div>
            <div className="bubbleContent">
                <div className="nickName">小熊</div>
                <div className="picBox" style={{backgroundImage:'url('+props.item.filePath+')'}}>
                </div>
            </div>
        </div>
    )
}


