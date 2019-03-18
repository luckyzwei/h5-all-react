import React,{Component} from 'react'
import './index.scss'
import LoginModule from './LoginModule'
// 103 = 手机号为注册
// 104 = 手机号重复
// 106 = 账号或密码错误
// 112 = 验证码过期
// 115 = 用户名已存在
// 116 = 验证码错误
// 117 = 账号或密码错误
// 118 = 用户未登录
// 119 = 密码错误
// 120 = 服务器异常

export default class LoginMain extends Component{
    clickHandle = (status) => {
        this.setState({status})
    }
    render(){
        const {history} = this.props
        return (
            <div className='login-container'>
                <div className="imgBox"/>
                <div className="formBox">
                    <div className='tabBox'>
                        <span className='active'>登录</span>
                    </div>
                    <LoginModule history={history} clickHandle={this.clickHandle}/>
                </div>
            </div>
        )
    }
}
