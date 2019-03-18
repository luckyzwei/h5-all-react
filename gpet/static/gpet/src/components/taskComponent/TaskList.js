import React,{Component} from 'react'
import {format_date}from '../../funStore/CommonFun'
export default class TaskList extends Component {
    render(){
        const {listData,goTaskContent} =this.props
        return (
            <div ref="wrapper" className="messList">
                {
                    listData.map((item,index)=>{
                        return <div className="cardBox" key={index} onClick={() => goTaskContent(item.task_id)}>
                            <div className="item">
                                <span className='createDate'>文章 {format_date(item.send_date,'MM/DD HH:MM')}</span>
                                <div className='fotter'>
                                    <span className="num">总计{item.group_count}个群</span>
                                    {
                                        //1 发送成功 2 发送失败
                                        item.send_flag === 2
                                            ? <span className='msgtype msgWait'>待发送</span>
                                            : <span className='msgtype msgAlready'>已发送</span>
                                    }
                                </div>
                            </div>
                            <div className="item">
                                <span className="jumpArrow"/>
                            </div>
                        </div>
                    })
                }
            </div>
        )
    }
}