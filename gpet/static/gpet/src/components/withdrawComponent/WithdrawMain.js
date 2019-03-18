import React, { Component } from 'react'
import Withdraw from './Withdraw'
export default class WithdrawMain extends Component {
    constructor(props){
        super(props)
        this.state = {}
    }
    componentDidMount(){
        document.title = '提现'
    }
    render(){
        return(
            <div className='gp-container' style={{position:'relative'}}>
                <Withdraw />
            </div>
        )
    }
}