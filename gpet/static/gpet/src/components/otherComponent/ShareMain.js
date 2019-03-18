import React, { Component } from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {WXsharing} from "../../funStore/WXsharing";
import {saveCookie,getCookie} from "../../funStore/CommonFun";
import {get_userId, get_porterUrl} from '../../funStore/CommonPort'
import AuthProvider from "../../funStore/AuthProvider";
WXsharing()
export default class ShareMain extends Component {
    constructor(props){
        super(props)
        this.state = {
            modalShow: true,
            posterUrl: '',
            pageLoad: true
        }
        this.hideModal = this.hideModal.bind(this)
    }
    componentDidMount(){
        document.title = '收徒'
        let accessToken = getCookie('access_token',1*3600*1000)
        if(accessToken===null|| accessToken === 'null'){
            AuthProvider.onLogin(getCookie('union_id')).then(res => {
                this.handleUpdate()
            })
        }else{
            this.handleUpdate()
        }
    }
    handleUpdate=()=>{
        let sharingUserId = getCookie('sharing_user_id')
        if (sharingUserId === null || sharingUserId === 'null') {
            this.requestUserId()
        }else{
            this.getPorterUrl(sharingUserId)
        }
    }

    getPorterUrl=(user_id)=>{
        get_porterUrl(user_id).then(res=>{
            this.setState({
                posterUrl: res,
                pageLoad: false
            })
        })
    }

    // 获取当前用户的UserId
    requestUserId() {
        get_userId(resData=>{
            saveCookie('sharing_user_id',resData.data)
            this.getPorterUrl(resData.data)
        })
    }
    hideModal(e){
        e.preventDefault()
        this.setState({
            modalShow: false
        })
    }
    render(){
        const {modalShow,posterUrl,pageLoad}= this.state
        return(
            pageLoad?
            <LoadingAnimationA />
            :<div className='gp-container'>
                <div className="share-wrapper">
                    <div className="mask"/>
                    <img src={posterUrl?posterUrl:"/images/bj/post_bg.png"} alt=""/>
                    {
                        modalShow
                        ?<div className="modalWrapper" onClick={this.hideModal}>
                            <div className="modalBox">
                                <div className="fingerPrint"/>
                                <p>长按图片发送给朋友<br/>或保存图片发送朋友圈</p>
                            </div>
                        </div>
                        :null
                    }
                    <img className="hide" src={posterUrl?posterUrl:"/images/bj/post_bg.png"} alt="" onClick={this.hideModal}/>
                </div>
            </div>
        )
    }
}
