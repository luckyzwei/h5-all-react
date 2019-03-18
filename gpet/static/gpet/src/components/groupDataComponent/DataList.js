import React,{Component} from 'react'
import DataItem from './DataItem'

export default class DataList extends Component {
    scrollHandle = () => {
        let ele = this.refs.wrapper
        const {scrollTop,scrollHeight,offsetHeight} = ele
        if(scrollHeight-scrollTop-offsetHeight<500) {
            this.props.requestData()
        }
    }
    render(){
        const {data} = this.props
        return (
            <div ref="wrapper" className="dataList" onScroll={this.scrollHandle}>
                {
                    data.map((v,i)=>{
                        return  <DataItem key={i} data={v}/>
                    })
                }
            </div>
        )
    }
}