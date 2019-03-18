import React,{Component} from 'react'
export default class KeyWItem extends Component {
    render() {
        const {item,handleOpen,goDetails} =this.props
        return(
            <div className='keyword-item'>
                <div className="title" onClick={(e)=>{e.stopPropagation();goDetails(item.batch_id)}}>
                    <div className='name'>关键词</div>
                    <div className='keyword'>
                        {
                            item.keywords.map((v,i)=>{
                                return <span key={i}>{v}</span>
                            })
                        }
                    </div>
                    <div className='jumpArrow'/>
                </div>
                <div className="footer">
                    <div className='info'>
                        <span>总计{item.bind_group_counts}个群</span>
                        <span>触发次数：{item.trigger_times}次</span>
                    </div>
                    <div className='delBtn' onClick={(e)=>{e.stopPropagation();handleOpen(item.batch_id)}}>
                        删除
                    </div>

                </div>
            </div>

        )
    }
}
