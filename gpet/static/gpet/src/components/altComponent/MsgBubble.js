import React from 'react'
import ImgMsgBox from './ImgMsgBox'
import MsgTransform from './MsgTransform'
const MsgBubble = ({msg,showPreviewImg,msgId}) => {
    const type = msg.content.type
    const judagebyId = msg.is_master  //is_master true:发消息的用户
    const msgInfo = msg.content
    // const memInfo = msg.memInfo
    switch(type){
        // 普通文本消息
        case 3: 
            let content = MsgTransform(msgInfo.content,[])
            return (
                !judagebyId
                ?<div className="friendMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="friendMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <div className="msgBox">
                            <pre dangerouslySetInnerHTML={{__html: content}} />
                        </div>
                    </div>
                </div>
                :<div className="selfMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="selfMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <div className="msgBox">
                            <pre dangerouslySetInnerHTML={{__html: content}} />
                        </div>
                    </div>
                </div>
            )
        //图片
        case 8:
            return (
                !judagebyId
                ?<div className="friendMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="friendMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <ImgMsgBox src={msgInfo.content} showPreviewImg={showPreviewImg} alt=''/>
                    </div>
                </div>
                :<div className="selfMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="selfMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <ImgMsgBox src={msgInfo.content} showPreviewImg={showPreviewImg} alt=''/>
                    </div>
                </div>
            )
        default:
            return (
                !judagebyId
                ?<div className="friendMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="friendMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <div className="msgBox">
                            <pre dangerouslySetInnerHTML={{__html: '当前版本暂不支持查看此消息'}} />
                        </div>
                    </div>
                </div>
                :<div className="selfMsgBubble" id={msgId}>
                    <div className="avatarBox">
                        <img src={msg.head_url?msg.head_url:'/images/icon/uesrIcon.png'} alt=''/>
                    </div>
                    <div className="selfMsgBox">
                        <div className="nickName">{msg.nickname}</div>
                        <div className="msgBox">
                            <pre dangerouslySetInnerHTML={{__html: '当前版本暂不支持查看此消息'}} />
                        </div>
                    </div>
                </div>
            )
    }
}

export default MsgBubble