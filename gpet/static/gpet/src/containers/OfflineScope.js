import React, {Component } from 'react'
import {getSearch} from '../funStore/CommonFun'
export default class OfflineScope extends Component{
    componentDidMount(){
        document.title='维护中'
    }
    render(){
        console.log(this.props.history,'history')
        return <div className='gp-container'>
            <div className="error-wrapper">
                <p>系统正在维护中<br/>预计将于{decodeURI(getSearch().time)}结束!</p>
                <img className='img404' src={"/images/icon/pic_offline.png"} alt=""/>
            </div>
        </div>
    }
}
