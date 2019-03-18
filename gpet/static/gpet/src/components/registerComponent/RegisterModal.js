import React, {Component} from 'react'
import {phoneVerify, codeVerify, sendEvent} from "../../funStore/CommonFun";
import {tongji} from "../../constants/TrackEvent";
import ButtonLoading from '../shareComponent/ButtonLoading'
import {get_verify_code, fill_Phone} from '../../funStore/CommonPort'
import Message from '../shareComponent/Message'
import './index.scss'
export default class RegisterModal extends Component{
    constructor(props) {
        super(props)
        this.state = {
            accountInfo: '',
            params: {
                phone: "",
                code: ""
            },
            pageLoading: true,
            isGetCode: false,
            timeLimit: 60,
            codeError: false,
            codeDisabled: true,
            btnLoading: false,
        }
        this.handleChange = this.handleChange.bind(this)
        this.getCode = this.getCode.bind(this)
        this.timeCount = this.timeCount.bind(this)
        this.requestCode = this.requestCode.bind(this)
        this.registerHandle = this.registerHandle.bind(this)
    }

    componentWillUnmount() {
        clearInterval(this.countTimer)
    }

    getCode() {
        const {params} = this.state
        if (phoneVerify(params.phone)) {
            this.setState({
                isGetCode: true
            }, this.timeCount)
            // 获取手机验证码
            this.requestCode()
        }
    }

    timeCount() {
        let {timeLimit} = this.state
        const self = this
        this.countTimer = setTimeout(() => {
            if (timeLimit > 1) {
                self.setState({
                    timeLimit: timeLimit - 1
                }, self.timeCount)
            } else {
                self.setState({
                    isGetCode: false,
                    timeLimit: 60
                })
            }
        }, 1000)
    }

    requestCode() {
        let phone = this.state.params.phone
        get_verify_code(phone).then(resData => {
            if (resData.code !== 1200) {
                sendEvent("messages", {msg: "获取验证码失败", status: 200})
                this.setState({
                    isGetCode: false,
                    timeLimit: 60
                })
                clearInterval(this.countTimer)
            }
        })
        tongji('phone_getVerifyCode')
    }

    //补全群宠用户信息手机号
    registerHandle() {
        const {params} = this.state
        this.setState({
            btnLoading: true
        })
        fill_Phone(params).then(resData => {
            if (resData.code === 1200) {
                // 注册成功后，保存用户ID 登录
                sendEvent("messages", {msg: "提交成功", status: 200})
                setTimeout(() => {
                    this.props.changeAmountData()
                }, 1500)
                // 2301:验证码错误 2302:验证码过期
            } else if (resData.code === 2301) {
                sendEvent("messages", {msg: "验证码错误", status: 200})
            } else if (resData.code === 2302) {
                sendEvent("messages", {msg: "验证码过期", status: 200})
            } else if (resData.code === 2303) {
                sendEvent("messages", {msg: "手机号已注册", status: 200})
            } else {
                sendEvent("messages", {msg: "提交失败", status: 200})
            }
            this.setState({btnLoading: false})
        })
        tongji('phone_buQuanPhone')

    }

    handleChange(e) {
        const {params} = this.state
        params[e.target.name] = e.target.value
        this.setState({params})
    }


    submitVerifyHandle = () => {
        const {params} = this.state
        let flag = true
        if (!phoneVerify(params.phone) || !codeVerify(params.code)) {
            flag = false
        }
        return flag
    }

    render() {
        const {isGetCode, btnLoading, timeLimit, params} = this.state
        let btnDisabled = this.submitVerifyHandle()
        return (
            <div className='modalWrapper'>
                <div className='modalBox writeBox registerModal'>
                    <div className="register-wrapper">
                        <div className="inputBox">
                            <input type="text" maxLength={11} value={params.phone} placeholder="请输入手机号"
                                   name='phone' autoComplete='off'
                                   onChange={(e) => this.handleChange(e)}/>
                        </div>
                        <div className="inputBox">
                            <input type="text" maxLength={6} placeholder='请输入验证码' name='code'
                                   value={params.code} autoComplete="off"
                                   onChange={(e) => this.handleChange(e)}/>
                            {
                                !isGetCode
                                    ? <div className={`btnCode ${phoneVerify(params.phone) ? '' : 'disable'}`}
                                           onClick={this.getCode}>获取验证码</div>
                                    : <div className="btnCode disable">{timeLimit}s</div>
                            }
                        </div>
                        <div className="btnBox">
                            <button className={`submitBtn ${!btnDisabled ? '' : 'disable'}`} disabled={!btnDisabled}
                                    onClick={btnDisabled ? this.registerHandle : null}>
                                {
                                    btnLoading ? <ButtonLoading text={'提交中'} color={'#fff'}/> : '确认'
                                }
                            </button>
                        </div>
                    </div>
                    <div className='icon-cross closeBtn' onClick={this.props.hideRegisterModel}/>
                    <Message/>
                </div>
            </div>

        )
    }
}
