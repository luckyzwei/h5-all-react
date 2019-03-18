import React,{Component} from 'react'

let AmountType = {
    0:'拉群',
    1:'资讯点击',
    2:'徒弟徒孙',
    3:'领养费用',
    4:'其他'
}


export default class ListItem extends Component {
    constructor(props){
        super(props)
        this.state = {
            height: 102,
            deltaHeight: 0
        }
        this.expandHandle = this.expandHandle.bind(this)
    }
    componentDidMount(){
        this.setState({
            deltaHeight: this.refs.detail.offsetHeight
        })
        this.refs.content.style.transition = 'all ease-in-out .3s'
    }
    expandHandle(e){
        e.stopPropagation()
        this.props.checkHandle(this.props.index)
    }
    render(){
        const {height,deltaHeight} = this.state
        const {index,checkIndex,isExpand,item} = this.props
        return (
            <li>
                <div ref="content" className="content" style={{height:isExpand&&checkIndex===index?height+deltaHeight+'px':height+'px'}}>
                    <div className="substract" onClick={this.expandHandle}>
                        <span className="date">{item&&item.day?item.day.replace(/-/g,'/'):''}</span>
                        <span className="money">{item?item.balance_detail<0?item.balance_detail:'+'+item.balance_detail:'0.00'}</span>
                        <span className={isExpand&&checkIndex===index?"downArrow up":"downArrow"}/>
                    </div>
                    <div ref="detail" className="detail">
                        {
                            item&&item.detail?item.detail.map((v,i)=>{
                                return <div className="info" key={i}>
                                    <span>{AmountType[v.slip_type]}</span>
                                    <span>{v?v.balance<0?v.balance:'+'+v.balance:'+0'}</span>
                                </div>
                            }):null
                        }
                    </div>
                </div>
            </li>
        )
    }
}
