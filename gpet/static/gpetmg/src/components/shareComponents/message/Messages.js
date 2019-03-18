import React, { Component } from 'react'
import "./message.scss"

let setTimeOuttimer;

export default class Messages extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showStatus: false,
            showText: null,
            reqStatus: false
        }
    }
    getMessage = (res) => {
        let _this = this;
        clearTimeout(setTimeOuttimer);
        _this.setState({
            showStatus: true,
            showText: res.newValue.msg,
            reqStatus: res.newValue.status
        })
        if (res.newValue.status !== 202) {
            setTimeOuttimer = setTimeout(() => {
                _this.setState({
                    showStatus: false,
                    reqStatus: false,
                    showText: null
                })
            }, res.newValue.timer || 2000);
        }
    }
    componentDidMount() {
        window.addEventListener("messages", res => { this.getMessage(res) })
    }

    componentWillUnmount() {
        window.removeEventListener("messages", res => { this.getMessage(res) })
    }

    render() {
        const { showStatus, showText, reqStatus } = this.state;
        return (<div className="messages-main">{
            showStatus ? <div
                className={
                    reqStatus === 200 ?
                        "messages-main-content success" :
                        (reqStatus === 201 ? "messages-main-content warning" :
                            (reqStatus === 202 ? "messages-main-content loading" :
                                (reqStatus === 203 ? "messages-main-content error" :
                                    "messages-main-content other")))
                }
            >
                {
                    reqStatus === 202 ?
                        <img src={process.env.PUBLIC_URL+'/images/icon/loading.svg'} className='messages-main-icon' alt=''/> :
                        <span
                            className={
                                reqStatus === 200 ?
                                    "messages-main-icon success" :
                                    (reqStatus === 201 ? "messages-main-icon warning" :
                                        (reqStatus === 202 ? "messages-main-icon loading" :
                                            (reqStatus === 203 ? "messages-main-icon error" :
                                                "messages-main-icon other")))
                            }
                        />
                }
                <span>{showText}</span>
            </div> : ""
        }</div>)
    }
}




/**
 * =>timer参数非必传，默认2s;
 * success sendEvent("messages",{msg:"",status:200,timer:2000})
 * worning sendEvent("messages",{msg:"",status:201,timer:2000})
 * loading sendEvent("messages",{msg:"",status:202,timer:9999})
 * error   sendEvent("messages",{msg:"",status:203,timer:2000})
 */