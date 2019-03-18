import React, {Component} from 'react'
import {tongji} from '../constants/TrackEvent'
import {deleteCookie} from '../funStore/CommonFun'
import {history} from '../index'
export default class Error extends Component{
    handleRefresh=()=>{
        //清空cookie 跳回上一页 重新登录
        deleteCookie('access_token')
        history.goBack();
        tongji('error_refresh')
    }

    render(){
        return(
            <div style={{height:'100%'}}>
                <div className='gp-container'>
                    <div className="error-wrapper">
                        <p>主人网络有点差哦！<br/>请稍后再试!</p>
                        <img className='img404' src={"/images/icon/pic_404.png"} alt=""/>
                        <div className="refreshBtn" onClick={this.handleRefresh}>刷新</div>
                    </div>
                </div>
            </div>
        )
    }
}