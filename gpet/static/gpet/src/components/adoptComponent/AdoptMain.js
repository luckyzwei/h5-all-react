import React, {Component} from 'react'
import AuthProvider from '../../funStore/AuthProvider'
import {getSearch} from '../../funStore/CommonFun'
import {Error1, Error2, Error3} from './AdoptError'
import AccountInfo from '../../funStore/AccountInfo';
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {is_registered, get_robot} from '../../funStore/CommonPort'
import './index.scss'

export default class AdoptMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            view: 'ADD',
            accountInfo: null,
            robotInfo: null,
            pageLoad: true
        }
        this.weChatHandle = this.weChatHandle.bind(this);
        this.getRobot = this.getRobot.bind(this);
        this.changeView = this.changeView.bind(this)
    }

    componentDidMount() {
        document.title = "添加好友"
        this.weChatHandle()
    }

    weChatHandle() {
        const {history} = this.props
        // 获取unionid
        AccountInfo.requestUnionId().then(res => {
            const accountInfo = res
            // 获取unionid之后判断是否注册
            this.setState({accountInfo: res})
            // 获取unionid之后判断用户是否注册
            is_registered('/' + accountInfo.unionid + '/registered').then(resData => {
                if (resData.data) { // True：注册,False:没注册
                    //注册成功，登录
                    AuthProvider.onLogin(accountInfo.unionid).then(res => {
                        if (res.code === 1200) {
                            history.push('/grouppet/home')
                        } else {
                            // 登录失败,获取群宠机器人
                            history.push('/grouppet/error')
                        }
                    })
                } else {
                    // 没有注册，获取机器人/
                    this.getRobot()
                }
            })
        })
    }

    getRobot() {
        // 登录失败,获取群宠机器人
        const {accountInfo} = this.state;
        let params = getSearch()
        let data = {
            open_id: accountInfo.openid,
            union_id: accountInfo.unionid,
            sharing_user_id: params.sharing_user_id ? params.sharing_user_id : null,
            channel: params.channel ? params.channel : ''
        }
        get_robot(data).then(resData => {
            if (resData.code === 1200) {
                this.setState({
                    robotInfo: resData.data,
                    pageLoad: false
                })
            } else if (resData.code === 1600) { //1404 机器人没有找到 1600 没有可分配的机器人
                // 今天额度已经用完
                this.setState({
                    view: 'ERROR1',
                    pageLoad: false
                })
            } else {
                // 页面报错了
                this.setState({
                    view: 'ERROR3',
                    pageLoad: false
                })
            }
        })
    }

    changeView(view) {
        this.setState({
            view: view
        })
    }

    render() {
        const {view, robotInfo, pageLoad} = this.state;
        let viewController
        switch (view) {
            case 'ADD':
                viewController = <div className="adopt-wrapper">
                    <div className="codeBox">
                        <img className="qrcode" src={robotInfo&&robotInfo.qr_code} alt=""/>
                    </div>
                </div>
                break;
            case 'ERROR1':
                viewController = <Error1/>
                break;
            case 'ERROR2':
                viewController = <Error2/>
                break;
            case 'ERROR3':
                viewController = <Error3/>
                break;
            default:
                break;
        }
        return (
            pageLoad ? <LoadingAnimationA/>
                : <div className='gp-container'>
                    {viewController}
                </div>
        )
    }
}

