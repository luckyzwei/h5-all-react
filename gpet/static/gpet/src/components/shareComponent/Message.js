import React, { Component } from 'react'
let setTimeOuttimer;

export default class Message extends Component {
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
            }, res.newValue.timer || 1500);
        }
    }
    componentDidMount() {
        window.addEventListener("messages", res => { this.getMessage(res) })
    }

    componentWillUnmount() {
        window.removeEventListener("messages", res => { this.getMessage(res) })
    }
    render() {
        const { showStatus, showText} = this.state;
        const {styleTop} =this.props
        return (
            showStatus? <div className={`new-verifyTipBox animated ${showStatus?'fadeIn':'fadeOut'}` } style={styleTop?styleTop:{}}>{showText}</div> : null
        )
    }
}




// /**
//  * =>timer参数非必传，默认2s;
//  * success sendEvent("messages",{msg:"",status:200,timer:2000})
//  * worning sendEvent("messages",{msg:"",status:201,timer:2000})
//  * loading sendEvent("messages",{msg:"",status:202,timer:9999})
//  * error   sendEvent("messages",{msg:"",status:203,timer:2000})
//  */