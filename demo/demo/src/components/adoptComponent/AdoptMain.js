import React, {Component} from 'react'
import {Error1, Error2, Error3} from './AdoptError'
import AccountInfo from '../../funStore/AccountInfo';
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {is_registered, get_robot} from '../../funStore/CommonPort'
import './index.css'

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

        //本地
        // let unionid= getCookie('unionId_demo')
        // this.getRobot(unionid)

        AccountInfo.requestUnionId().then(res => {
            const accountInfo = res
            // 获取unionid之后判断是否注册
            this.setState({accountInfo: res})
            is_registered(accountInfo.unionid).then(resData => {
                if (resData.data) { // True：注册,False:没注册
                    //注册成功，登录
                    history.push('/demo/home')
                } else {
                    /// 没有注册，获取机器人/
                    this.getRobot(accountInfo.unionid)
                }
            })
        }).catch(err => {
            this.props.history.push('/demo/error')
        })
    }

    getRobot(unionid) {
        // 登录失败,获取群宠机器人
        get_robot(unionid).then(resData => {
            console.log(resData,'resData===')
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
                viewController =
                   <div className="qrcode-content">
                       <div className="qrcode-title">
                           <img className="head_url" src={robotInfo&&robotInfo.head_url}  alt=""/>
                           <div className="group-word">
                               <div className="name">
                                   <span>{robotInfo&&robotInfo.name}</span>
                                   <span>(群主专属)</span>
                               </div>
                               <div className="des">群主开心赚钱，群友也能得福利</div>
                           </div>
                       </div>
                       <div className="qrcode-img">
                           <img className="qrcode" src={robotInfo&&robotInfo.qr_code} alt=""/>
                       </div>
                       <div className="des-buttom">扫一扫上面的二维码图案，加我微信</div>
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
                : <div className='adopt-wrapper'>
                    {viewController}
                </div>
        )
    }
}

