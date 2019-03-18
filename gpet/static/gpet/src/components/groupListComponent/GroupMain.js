import React, { Component } from 'react'
import GroupList from './GroupList'
export default class GroupMain extends Component {
    componentDidMount(){
        document.title = '群列表'
    }
    render(){
        return(
            <div className='gp-container' style={{background: "#F7F8F9"}}>
                <GroupList/>
            </div>
        )
    }
}