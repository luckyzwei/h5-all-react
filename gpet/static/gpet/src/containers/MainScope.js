import React,{Component} from 'react'
import { Route} from 'react-router'
import Loadable from 'react-loadable'
import LoadingAnimationA from '../components/shareComponent/LoadingAnimationA'
import {APP_ID} from '../constants/OriginName'
import AuthProvider from '../funStore/AuthProvider'
import {WXsharing, WXconfig} from '../funStore/WXsharing'
import {getQueryString,saveCookie,getCookie} from '../funStore/CommonFun'
import AccountInfo from '../funStore/AccountInfo' //用户信息
import {is_registered, get_userId, fill_userInfo, refresh_user_info, check_auth, home_group_count, is_received_red} from '../funStore/CommonPort'

const Loading = () => <div className='verticalCenter'><LoadingAnimationA/></div>
const HomeMain = Loadable({loader:()=>import('../components/homeComponent/HomeMain'), loading:()=><Loading/>})
const GroupMain = Loadable({loader:()=>import('../components/groupListComponent/GroupMain'), loading:()=><Loading/>})
const DiscipleMain = Loadable({loader:()=>import('../components/discipleComponent/DiscipleMain'), loading:()=><Loading/>})
const ShareMain = Loadable({loader: () => import('../components/otherComponent/ShareMain'), loading: ()=> <Loading/>,});
const ImportMain = Loadable({loader:()=>import('../components/otherComponent/ImportMain'), loading:()=><Loading/>})
const ProfitMain = Loadable({loader: () => import('../components/profitComponent/ProfitMain'), loading: ()=><Loading/>,});
const WithdrawMain = Loadable({loader: () => import('../components/withdrawComponent/WithdrawMain'), loading: ()=><Loading/>,});
const TaskScope = Loadable({loader:()=>import('../components/taskComponent/TaskMain'), loading:()=><Loading/>})
const TaskDetails = Loadable({loader:()=>import('../components/taskComponent/TaskDetails'), loading:()=><Loading/>})
const GroupDataMain = Loadable({loader:()=>import('../components/groupDataComponent/GroupDataMain'), loading:()=><Loading/>})
const CreateMessMsg = Loadable({loader:()=>import('../components/messMsgComponent/CreateMessMsg'), loading:()=><Loading/>})
const MessMsgScope = Loadable({loader:()=>import('../containers/MessMsgScope'), loading:()=><Loading/>})
const MessMsgContent = Loadable({loader:()=>import('../components/messMsgComponent/MessMsgContent'), loading:()=><Loading/>})
const AltMeScope = Loadable({loader:()=>import('../containers/AltMeScope'), loading:()=><Loading/>})
const KeyWordScore = Loadable({loader:()=>import('./KeyWordScore'), loading:()=><Loading/>})
const CreateWelmsg = Loadable({loader:()=>import('../components/otherComponent/CreateWelmsg'), loading:()=><Loading/>})
const QuestionMain = Loadable({loader:()=>import('../components/questionComponent/QuestionMain'), loading:()=><Loading/>})
const FeedbackMain = Loadable({loader:()=>import('../components/questionComponent/FeedbackMain'), loading:()=><Loading/>})
const RedPacket = Loadable({loader:()=>import('../components/registerComponent/RedPacket'), loading:()=><Loading/>})
const HelpMain = Loadable({loader:()=>import('../components/otherComponent/helpScope/HelpMain'), loading:()=><Loading/>})
const StarMain = Loadable({loader:()=>import('../components/otherComponent/starScope/StarMain'), loading:()=><Loading/>})
const GoHomeScope = Loadable({loader:()=>import('../containers/GoHomeScope'), loading:()=><Loading/>})
const Message = Loadable({loader:()=>import('../components/shareComponent/Message'), loading:()=><Loading/>})

export default class MainScope extends Component{
    constructor(props) {
        super(props)
        this.requestOutline = this.requestOutline.bind(this)
        this.getAccountInfo = this.getAccountInfo.bind(this)
        this.login = this.login.bind(this)
        this.refreshUserInfo = this.refreshUserInfo.bind(this)
        this.requestUserId = this.requestUserId.bind(this)
        this.checkAuth = this.checkAuth.bind(this)
        this.state = {
            redPacket:false,
            guide: false,
            notHomeguide:false,
            params: {},
            pageLoad: true,
            outlineInfo:'',
        }
    }

    componentDidMount() {
        //授权之后登录   //测试时cookie中添加unionId和改变Domain为localhost
        this.getAccountInfo()
        WXconfig()
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.location.pathname !== nextProps.location.pathname) {
            WXconfig()
        }
    }

    //尝试登录
    getAccountInfo() {
        let unionId = getCookie('union_id')
        // 获取unionid,并保存
        if (unionId && unionId !== 'null') {
            this.login(unionId)
        } else {
            // 不存在unionId,先获取，在登录
            AccountInfo.requestUnionId().then(res => {
                this.setState({
                    accountInfo: res,
                    params: {
                        "headUrl": res.headimgurl,
                        "nickName": res.nickname,
                        "openId": res.openid,
                        "unionId": res.unionid,
                        "sharingUserId": getQueryString('sharingUserId')!==undefined?getQueryString('sharingUserId'):'',
                        'userId':getQueryString('userId'),
                        "appId": APP_ID,
                    }
                })
                // 获取unionid之后登录
                this.login(res.unionid)
            }).catch(err => {
                this.props.history.push('/grouppet/error')
            })
        }
    }

    //根据unionid登录
    login(unionid) {
        // 获取unionid之后判断用户是否注册／是否有补全信息
        is_registered('/'+unionid+'/registered').then(resData => {
            if (resData.data) { // True：注册,False:没注册
                //已注册，登录，获取信息
                this.requestOutline(unionid)
            } else {
                //没有注册，根据userId判断是否补全信息
                this.fillMsgUserId(unionid)
            }
        })
    }

    //根据userId 判断是否补全信息
    fillMsgUserId = (unionid) => {
        const userId = getQueryString('userId')
        let params = {
            "appid": APP_ID,
            "head_url": getCookie('head_url'),
            "nick_name": getCookie('nick_name'),
            "open_id": getCookie('open_id'),
            "union_id": getCookie('union_id'),
        }
        // 判断补全群宠用户信息是否已补全
        if (userId) {
            // 没有补全信息 需要补全信息
            // console.log(params,'补全信息params')
            fill_userInfo(userId,params).then(resData => {
                if (resData.code === 1200) {
                    // 补全信息成功,登录
                    this.requestOutline(unionid)
                } else {
                    // 注册不成功
                    this.props.history.push('/grouppet/error')
                }
            })
        } else {
            // 不存在userId,跳转添加好友
            this.props.history.push('/grouppet/adopt')
        }
    }

    //onLogin 登录
    requestOutline(unionid) {
        AuthProvider.onLogin(unionid).then(res => {
            // 判断是否有领取红包
            this.isReceiveRedPacket()
            // 获取群宠概要
            this.getGroupData()
            // 根据token获取用户的userId  (sharingUserId)
            this.requestUserId()
            // 检查账号(用户)是否封掉 block_verify
            this.checkAuth()
            // 每次登录成功后刷新用户信息
            this.refreshUserInfo()
        })
    }
    getGroupData=()=>{
        home_group_count().then(resData=>{
            if(resData.code===1200){
                this.setState({
                    outlineInfo: resData.data,
                    pageLoad:false
                })
            }
        })
    }

    isReceiveRedPacket=()=>{
        //1.先判断是否有领取红包 "data": True/False //True已经领取过，False未领取
        is_received_red().then(res=>{
            if(res.data){
                // 已经领取过红包
            }else{
                // 没有领取过红包,第一次登录
                this.setState({
                    redPacket:true //有红包
                })
            }
        })
    }

    hideFirstGide=()=>{
        localStorage.removeItem('firstFlag')
        this.setState({
            guide: false //引导
        })
    }

    hideRedPacket=()=> {
        this.setState({
            guide: true, //引导
            redPacket:false,
        })
    }

    //获取用户的userId
    requestUserId() {
        // 获取当前人的UserId，用于微信右上角分享
        get_userId().then(resData => {
            saveCookie('sharing_user_id',resData.data)
            WXsharing()
        })
    }

    //刷新用户信息
    refreshUserInfo() {
        let unionId =  getCookie('union_id')
        let params = {
            "appid": APP_ID,
            "head_url": getCookie('head_url'),
            "nick_name": getCookie('nick_name'),
            "open_id": getCookie('open_id'),
        }
        refresh_user_info(unionId,params);
    }


    // 检查账号是否封掉 True：封号,False:正常
    checkAuth() {
        check_auth().then(resData=>{
            if(!resData.data) return
            if(resData.code === 1200 && resData.data){
                this.props.history.push('/grouppet/noauth')
            }
        })
    }

    render() {
        const {guide, pageLoad,outlineInfo} = this.state
        const {history} =this.props
        const propsData = {
            guide: guide,
            pageLoad:pageLoad,
            outlineInfo:outlineInfo,
            hideFirstGide:this.hideFirstGide,
        }
        return (
            <div>
                {/*首页*/}
                <Route path="/grouppet/home" render={props => (<HomeMain {...props} {...propsData}/>)}/>
                {/*群列表*/}
                <Route path="/grouppet/group" component={GroupMain}/>
                {/*徒弟徒孙*/}
                <Route path="/grouppet/disciple" component={DiscipleMain}/>
                {/*拉群*/}
                <Route path="/grouppet/import" component={ImportMain}/>
                {/*分享*/}
                <Route path="/grouppet/share" component={ShareMain}/>
                {/*群收益*/}
                <Route path="/grouppet/profit" component={ProfitMain}/>
                {/*提现*/}
                <Route path="/grouppet/withdraw" component={WithdrawMain}/>
                {/*文章投放*/}
                <Route path="/grouppet/tasknote" component={TaskScope}/>
                {/*文章投放详情*/}
                <Route path="/grouppet/taskdetails/:id?" component={TaskDetails}/>
                {/*群数据*/}
                <Route path="/grouppet/data" component={GroupDataMain}/>
                {/*欢迎语*/}
                <Route path="/grouppet/createwelcome" component={CreateWelmsg}/>
                {/*新建群发消息*/}
                <Route path="/grouppet/createmess" component={CreateMessMsg}/>
                {/*群发消息详情*/}
                <Route path="/grouppet/messmsgetails/:id" component={MessMsgContent}/>
                {/*群发消息列表*/}
                <Route path="/grouppet/messmsg" component={MessMsgScope}/>
                {/*@消息*/}
                <Route path="/grouppet/altme" component={AltMeScope}/>
                {/*关键词*/}
                <Route path="/grouppet/keyword" component={KeyWordScore}/>
                {/*常见问题*/}
                <Route path="/grouppet/question" component={QuestionMain}/>
                {/*问题反馈*/}
                <Route path="/grouppet/feedback" component={FeedbackMain}/>
                {/*赚钱攻略／红包攻略*/}
                <Route path="/grouppet/help" component={HelpMain}/>
                {/*群星级/舒适度说明*/}
                <Route path="/grouppet/star" component={StarMain}/>
                {
                    this.props.location.pathname === '/grouppet/home' ||
                    this.props.location.pathname === '/grouppet/share'
                        ? null : <GoHomeScope history={history}/>
                }
                {/*首次领红包*/}
                {
                    this.props.location.pathname === '/grouppet/star' ||
                    this.props.location.pathname === '/grouppet/home'
                        ? this.state.redPacket
                        ? <RedPacket
                            hideRedModel={this.hideRedPacket}/> : null : null

                }
                {
                    this.props.location.pathname === '/grouppet/createwelcome' ||
                    this.props.location.pathname === '/grouppet/withdraw' ||
                    this.props.location.pathname === '/grouppet/altme'
                        ? null : <Message/>
                }
            </div>
        )
    }
}
