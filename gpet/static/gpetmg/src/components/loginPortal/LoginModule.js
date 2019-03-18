import React, {Component} from 'react'
import Input from './input/Input'
import {LOGIN_USER} from '../../constants/OriginName'
export default class LoginModule extends Component {
    constructor(props) {
        super(props)
        this.state = {
            checkArr: [],
            checkFlag: false,
            params: {
                username: '',
                password: ''
            },
            tip: {
                username: '',
                password: ''
            },
            btnBlock: false
        }
    }

    inputHandle = (k, v) => {
        let {params} = this.state
        params[k] = v
        this.setState({params})
    }
    loginHandle = () => {
        let {params, btnBlock} = this.state
        this.setState({checkArr:[]})
        if (!this.veriftyHandle()) return
        if (btnBlock) return
        localStorage.setItem('gpet_mg_name',params.username)
        localStorage.setItem('gpet_mg_psd',params.password)
        this.setState({btnBlock: true})
        this.props.history.push('/gpetmg/review')
    }
    veriftyHandle = () => {
        let {params, tip, checkArr} = this.state
        checkArr = []
        tip = {
            username: '',
            password: ''
        }
        let flag = true
        // 用户名校验
        if (params.username.trim() === '') {
            flag = false
            tip.username = '用户名不能为空'
            checkArr.push('loginFlag')
        } else if (/[\u4e00-\u9fa5]/g.test(params.username)) {
            flag = false
            tip.username = '用户名不能包含中文'
            checkArr.push('loginFlag')
        } else if (params.username !== LOGIN_USER.username) {
            flag = false
            tip.username = '用户名错误'
            checkArr.push('loginFlag')
        }
        // 密码校验
        if (params.password.trim() === '') {
            flag = false
            tip.password = '密码输入不能为空'
            checkArr.push('pwdFlag')
        } else if (params.password !== LOGIN_USER.password) {
            flag = false
            tip.password = '密码错误'
            checkArr.push('pwdFlag')
        }
        this.setState({tip, checkArr})
        return flag

    }

    render() {
        const {params, checkArr, tip} = this.state
        return (
            <div>
                <Input type={'text'} placeholder={"输入用户名"} propsStyle={'icon-user'} tip={tip.username}
                       verifty={checkArr.indexOf('loginFlag') !== -1} inputHandle={this.inputHandle}
                       paramName={'username'} value={params.username}/>
                <Input type={'password'} placeholder={"输入密码"} propsStyle={'icon-password'} tip={tip.password}
                       verifty={checkArr.indexOf('pwdFlag') !== -1} inputHandle={this.inputHandle} paramName={'password'}
                       value={params.password}/>
                <div ref="button" className="loginBtn animated faster" onClick={this.loginHandle}>
                    登录
                </div>
            </div>
        )
    }
}