import React,{Component} from 'react'
import { Text,Link,Wxapp,Pic } from "../shareComponent/msgType/MsgTypeWapp";
import {format_date} from '../../funStore/CommonFun'
export default class PastDetails extends Component {
    render(){
        const {data} =this.props
        return  (
            <div className='new-messMsgList'>
                <div className="header">
                    <div className="title"/>
                </div>
                <div className='new-messMsgContent'>
                    <div className="messContent">
                        <div className="title">文章 {data.send_date!=null?format_date(data.send_date,'MM/DD HH:MM'):''}</div>
                        <div className='content'>
                            <div className="content-title">群发内容</div>
                            <div className="msgtype-content-info">
                                <div className="taskTitle">
                                    <img src={"/images/banner/title6.png"} alt="" />
                                </div>
                                <div className="previewBox">
                                    {
                                        data!=null&&data.materials!=null?data.materials.map((material,i)=> {
                                            // 内容类型，1-文字；2-图片；3-链接；4-小程序
                                            return (
                                                material.type===1
                                                    ? <Text item={material} key={i}/>
                                                    :material.type===3
                                                    ? <Link item={material} key={i}/>
                                                    :material.type===4
                                                        ? <Wxapp item={material} key={i}/>
                                                        : material.type===2
                                                            ?<Pic item={material} key={i}/>:''
                                            )
                                        }):''
                                    }
                                </div>
                            </div>
                        </div>

                    </div>
                    {
                        data&&data.groups&&data.groups.length>0
                            ? <div className="messRange">
                                <div className="title">
                                    <span>投放范围</span>
                                </div>
                                <ul>
                                    {data.groups.map((item,index)=>{return  <li key={index}><span>{item}</span></li>})}
                                </ul>
                            </div>
                            :null
                    }
                </div>
            </div>
        )

    }
}
