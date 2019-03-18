import React,{Component} from 'react'
import {tongji} from '../../constants/TrackEvent'

export default class ProfitNewBox extends Component {
    goWithdraw=()=>{
        this.props.history.push('/grouppet/withdraw')
        tongji('profit_goTiXian')
    }
    render(){
        const {profit} = this.props
        return (
            <div className="profitBox">
                <div className="title">
                    当前余额(元)
                </div>
                <div className='moneyBox'>
                    <div className="money">{profit&&profit.amount&&profit.amount>0?profit.amount:'0.00'}</div>
                    <div className="withdrawBtn" onClick={this.goWithdraw}>立即提现</div>
                </div>
                <div className="detail">
                    <div className="item">
                        <p>累计收益(元)</p>
                        <p>{profit&&profit.balance&&profit.balance>0?profit.balance:'0.00'}</p>
                    </div>
                    <div className="line"/>
                    <div className="item">
                        <p>昨日收益(元)</p>
                        <p>{profit&&profit.yesterday_balance&&profit.yesterday_balance>0?profit.yesterday_balance:'0.00'}</p>
                    </div>
                </div>
            </div>
        )
    }
}
