import React,{Component} from 'react'
import {tongji} from '../../../constants/TrackEvent'
import './index.css'
export default class Index extends Component {
    goGroupList=(e)=>{
        e.stopPropagation()
        this.props.history.push('/grouppet/group')
        tongji('home_group_list')
    }
    goDisciple=(e)=>{
        e.stopPropagation()
        this.props.history.push('/grouppet/disciple')
        tongji('home_disciple_list')
    }
    render(){
        const {outlineInfo} = this.props
        return (
            <div className="peopleCardBox">
                <div className="item" onClick={this.goGroupList}>
                    <div className="peopleNum">
                        <span className="num">{outlineInfo&&outlineInfo.group_count?outlineInfo.group_count:0}</span>
                    </div>
                    <div className='peopleText'>
                        累计入群<span>(个)</span>
                    </div>
                </div>
                <span className='item-line'/>
                <div className='item' onClick={this.goDisciple}>
                    <div className="peopleNum">
                        <span className="num">{outlineInfo&&outlineInfo.disciples?outlineInfo.disciples:0}</span>
                    </div>
                    <div className='peopleText'>
                        徒弟徒孙<span>(人)</span> 
                    </div>
                </div>
            </div>
        )
    }
}
