import React, {Component} from 'react'
import MsgBubble from './MsgBubble'
import $ from 'jquery'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import Message from '../shareComponent/Message'
import {sendEvent} from '../../funStore/CommonFun'
import {tongji} from '../../constants/TrackEvent'//埋点监测
import {get_altmsg_content,alt_reply} from '../../funStore/CommonPort'
// MSG_TYPE  0 IM系统消息
// MSG_TYPE  1 IM群属性变更消息
// MSG_TYPE  2 IM群成员属性变更消息
// MSG_TYPE  3 群聊天消息
// MSG_TYPE  4 提问班长消息
// MSG_TYPE  5 红包消息
// MSG_TYPE  6 广告消息
// MSG_TYPE  7 关键字匹配消息
// MSG_TYPE  8 图片消息
// MSG_TYPE  9 语音消息
// MSG_TYPE  10  视频消息
// MSG_TYPE  11  未识别类型消息
// MSG_TYPE  12  其它类型消息

export default class AnswerBox extends Component {
    constructor(props) {
        super(props)
        this.state = {
            historyList: [],
            loading: true,
            memCode: '',
            promptValue: null,
            sendBlock: false
        }
        this.sendHandle = this.sendHandle.bind(this)
        this.requestHistory = this.requestHistory.bind(this)
        this.scrollHandle = this.scrollHandle.bind(this)
    }

    componentDidMount() {
        setTimeout(() => {
            this.refs.answerBox.style.height = 'calc(69vh)'
        }, 50);
        this.requestHistory()
    }
    requestHistory() {
        const {message} = this.props
        get_altmsg_content(`${message.group_code}/msg/${message.msg_id}/context`).then(resData => {
            // resData.data = resData.data.reverse() //reverse() 方法用于颠倒数组中元素的顺序。
            if (resData.code === 1200&&resData.data!=null&&resData.data.length>0) {
                let sliceBegin = resData.data.findIndex(v => v.id === message.msg_id)
                this.setState({
                    historyList: resData.data,
                    sliceBegin: sliceBegin,
                    loading: false,
                    memCode: resData.data.find(v => v.id === message.msg_id).mem_code,
                }, () => {
                    this.refs.msgFlowBox.scrollTop = 2
                })
            }
        })
    }

    //回复@消息 （发送）
    sendHandle() {
        const {sendBlock,memCode} = this.state
        const {message} = this.props
        const value = $('#msg_context').text()
        if (value === '') return
        if (sendBlock) return
        this.setState({sendBlock: true})
        let params = {
            group_code:message.group_code,
            mem_code:memCode,
            content:value,
            type:3
        }
        alt_reply(params).then(resData => {
            if (resData.code === 1200) {
                sendEvent("messages", {msg: "回复成功", status: 200})
                $('#msg_context').text('')
            } else if(resData.code === 2003){
                sendEvent("messages", {msg: "内容不符合安全标准", status: 201})
            }else {
                sendEvent("messages", {msg: "回复失败", status: 200})
            }
            this.setState({
                sendBlock: false
            })
        })
        tongji('@wo_send@msg')
    }

    scrollHandle(e) {
        e.stopPropagation()
        e.preventDefault()
        let {sliceBegin, historyList} = this.state
        let {msgFlowBox} = this.refs;
        let scrollTop = msgFlowBox.scrollTop;
        let scrollHeight = msgFlowBox.scrollHeight;
        let clientHeight = msgFlowBox.offsetHeight;
        if (scrollTop === 0) {
            // 下拉加载...
            console.log('下拉加载');
            if (sliceBegin > 0) {
                // slicePage-60
                this.setState({sliceBegin: sliceBegin - 30}, () => {
                    let itemTop = $("#" + historyList[sliceBegin < 0 ? 0 : sliceBegin].id)[0].offsetTop;
                    this.refs.msgFlowBox.scrollTop = itemTop
                })
                this.refs.msgFlowBox.scrollTop = this.refs.msgFlowBox.scrollTop+50;
            }

        } else if (scrollTop === scrollHeight - clientHeight) {
            // 上拉刷新...
            console.log('上拉刷新');
            if (sliceBegin + 60 < historyList.length) {
                // slicePage-60
                this.setState({sliceBegin: sliceBegin + 30}, () => {
                    let lastMsg = $("#" + historyList[sliceBegin + 60 > historyList.length - 1 ? historyList.length - 1 : sliceBegin + 59].id)[0]
                    let itemTop = lastMsg.offsetTop - this.refs.msgFlowBox.offsetHeight + lastMsg.offsetHeight;
                    this.refs.msgFlowBox.scrollTop = itemTop
                })
            }
        }
    }

    render() {
        const {historyList, sliceBegin, loading} = this.state
        const {showPreviewImg} = this.props
        return (
            <div className="expand answerList">
                <div className="answerBox" ref='answerBox'>
                    <div className="history" ref='msgFlowBox' onScroll={this.scrollHandle}>
                        {
                            loading
                                ? <LoadingAnimationA/>
                                :
                                historyList.slice(sliceBegin < 0 ? 0 : sliceBegin, sliceBegin + 60).map((v, i) => {
                                    return <MsgBubble key={i} msg={v} showPreviewImg={showPreviewImg}
                                                      msgId={v.id}/>
                                })
                        }
                    </div>
                    <div className="reply">
                        <pre id="msg_context" contentEditable={true}/>
                        <div className="button-blue sendBtn" onClick={this.sendHandle}>发送</div>
                    </div>
                </div>
                <Message/>
            </div>

        )
    }
}