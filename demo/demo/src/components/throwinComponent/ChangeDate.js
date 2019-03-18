import React,{Component} from 'react'

export default class ChangeDate extends Component {
    changeBoxHandle(item,index){
        var subscript = this.props.timeData
        subscript[index].selected = !item.selected
        this.props.changeDate(subscript)
    }

    confirmHandle(){
        let list = []
        this.props.timeData.forEach((item)=>{
            if(item.selected) list.push(item.date)
        })
        this.props.confirmHandle(list.length>0?list:null)
    }

    render(){
        const {hideHandle,timeData} =this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox changeTime">
                    {
                        timeData.map((item,index)=>{
                            return <div className='list' key={index} onTouchEnd={()=>{this.changeBoxHandle(item,index)}} >
                                <img src={process.env.PUBLIC_URL+`${!item.selected?'/images/icon/check.png':'/images/icon/checked.png'}`} alt="" />
                                <div className="date">每日 {item.date}</div>
                            </div>
                        })
                    }
                    <div className="line"/>
                    <div className="btnBox" onTouchEnd={this.confirmHandle.bind(this)}>确定</div>
                    <div className='icon-cross closeBtn' onClick={hideHandle}/>
                </div>
            </div>
        )
    }
}
