import React, {Component} from 'react'
import {Route} from 'react-router'
import {APP_ID} from '../constants/OriginName'
import HomeMain from '../components/homeComponent/HomeMain'
import PreviewMain from '../components/previewComponent/PreviewMain'
import ThrowinMain from '../components/throwinComponent/ThrowinMain'
import {getCookie,getQueryString} from '../funStore/CommonFun'
import AccountInfo from '../funStore/AccountInfo' //用户信息
import {is_registered,fill_userInfo,group_list} from '../funStore/CommonPort'

export default class MainScope extends Component {

    constructor(prosp){
        super(prosp)
        this.state={
            groupList:null
        }
        this.login = this.login.bind(this)
    }

    componentDidMount() {
        this.getAccountInfo()
    }

    getAccountInfo=()=>{
        let unionId = getCookie('unionId_demo')
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
                this.props.history.push('/demo/error')
            })
        }
    }

    //根据unionid登录
    login(unionid) {
        // 获取unionid之后判断用户是否注册／是否有补全信息
        is_registered(unionid).then(resData => {
            if (resData.data) { // True：注册,False:没注册
                //已注册，登录，获取信息
                this.getGroupList(unionid)
            } else {
                //没有注册，根据userId判断是否补全信息
                this.fillMsgUserId(unionid)
            }
        })
    }

    //用户补全信息
    fillMsgUserId = (unionid) => {
        let userId = getQueryString('userId')
        let params = {
            "user_id":userId,
            "union_id":getCookie('unionId_demo'),
            "head_url":getCookie('headUrl_demo'),
            "nick_name":getCookie('nickName_demo')
        }
        // 判断补全群宠用户信息是否已补全
        if (userId) {
            // 没有补全信息 需要补全信息
            // console.log(params,'补全信息params')
            fill_userInfo(params).then(resData => {
                console.log(resData,'resData')
                if (resData.code === 1200) {
                    // 补全信息成功,登录
                    this.getGroupList(unionid)
                } else {
                    // 注册不成功
                    this.props.history.push('/demo/error')
                }
            })
        } else {
            // 不存在userId,跳转添加好友
            this.props.history.push('/demo/adopt')
        }
    }

    getGroupList=(unionid)=>{
        group_list(unionid).then(res=>{
            this.setState({
                groupList:res.data
            })

        })

    }
    render() {
        const {groupList}=this.state
        const propsData={
            groupList:groupList
        }
        return (
            <div>
                {/*首页*/}
                <Route path="/demo/home" render={props => (<HomeMain {...props} {...propsData}/>)}/>
                {/*投放预览*/}
                <Route path="/demo/preview" component={PreviewMain}/>
                {/*投放设置*/}
                <Route path="/demo/throwin" component={ThrowinMain}/>
            </div>
        );
    }
}


