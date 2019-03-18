import React ,{Component} from 'react'
export default class FeedbackTable extends Component{
    render(){
        const {listData,pageInfo} =this.props
        return  <div className="contentTable">
            <table>
                <thead>
                <tr>
                    <td>
                        <div className="number">
                            <span>序号</span>
                        </div>
                    </td>
                    <td>用户手机号</td>
                    <td>用户昵称</td>
                    <td>类型</td>
                    <td>机器人code</td>
                    <td>机器人昵称及微信号</td>
                    <td>群名</td>
                    <td>备注</td>
                    <td>提交时间</td>
                </tr>
                </thead>
                <tbody>
                {
                    listData&&listData.map((listItem,index) => {
                        return (
                            <tr key={index}>
                                <td>
                                    <div className="number">
                                        <span>{index+1+pageInfo.current_page*pageInfo.page_size}</span>
                                    </div>
                                </td>
                                <td>{listItem.phone?listItem.phone:'-'}</td>
                                <td>{listItem.nickname?listItem.nickname:'-'}</td>
                                <td>{listItem.title?listItem.title:'-'}</td>
                                <td>{listItem.code?listItem.code:'-'}</td>
                                <td>{listItem.robot_info?listItem.robot_info:'-'}</td>
                                <td>{listItem.group_name?listItem.group_name:'-'}</td>
                                <td className='questionDesc'>
                                    {listItem.description?listItem.description.length>10?listItem.description.slice(0,10)+'...':listItem.description:'-'}
                                    <div className="detail">
                                        {listItem.description}
                                    </div>
                                </td>
                                <td>{listItem.create_date}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
            </table>
        </div>
    }


}