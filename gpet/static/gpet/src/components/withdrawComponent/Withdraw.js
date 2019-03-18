import React, {Component} from 'react'
import Certificate from './Certificate'
import WithdrawResult from './WithdrawResult'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import RegisterModal from '../registerComponent/RegisterModal'
import {tongji} from '../../constants/TrackEvent'
import ButtonLoading from '../shareComponent/ButtonLoading'
import {get_withdraw_data,request_withdraw} from '../../funStore/CommonPort'
import './index.scss'

const amountMap = [1, 20, 50, 100, 200, 500]
export default class Withdraw extends Component {
    constructor(props) {
        super(props)
        // 1，20，50，100，200，500
        this.state = {
            profitAll: null,//可提现金额
            errorCode: '',
            pageLoad: true,
            amountType: -1,
            amountArray: [{
                amount: 1,
                type: 0
            }, {
                amount: 20,
                type: 1
            }, {
                amount: 50,
                type: 2
            }, {
                amount: 100,
                type: 3
            }, {
                amount: 200,
                type: 4
            }, {
                amount: 500,
                type: 5
            }],
            isNewUser: '',   //true:旧用户 已经提过啦 不可提现 false:新用户 没有提现 可以提现啦
            isRegister: false,
            isWithdraw: true,

        }
        this.requestWithdraw = this.requestWithdraw.bind(this)
        this.hideResult = this.hideResult.bind(this)
        this.showResult = this.showResult.bind(this)
        this.selectType = this.selectType.bind(this)
    }

    componentDidMount() {
        this.getRequestInfo()
    }

    changeAmountData = () => {
        this.getRequestInfo()
        this.requestWithdraw()
    }

    getRequestInfo = () => {
        get_withdraw_data().then(resData=>{
            if (resData.code === 1200) {
                this.setState({
                    isNewUser: resData.data.is_withdrawed,
                    profitAll: resData.data,
                    pageLoad: false
                })

            }
        }).catch(req=>{
            this.setState({
                pageLoad: false
            })
        })
    }

    requestWithdraw() {
        let self = this
        const {amountType, isWithdraw} = this.state
        if (amountType === -1 ) return
        let balance = amountMap[amountType]
        if (isWithdraw)
            this.setState({isWithdraw: false})
            let parmas={balance: balance}
            request_withdraw(parmas).then(resData=>{
                if (resData.code === 1200) { //提现成功
                    this.showResult('success')
                    this.getRequestInfo()
                    this.setState({
                        amountType: -1,
                        isRegister:false,
                    })
                    tongji('withdraw_sucess_'+amountMap[amountType])
                } else if (resData.code === 2001) {//2001     # 缺失手机号信息
                    self.setState({
                        isRegister: true
                    })
                    tongji('withdraw_fill_phone_'+amountMap[amountType])
                } else if (resData.code === 2002) {//2002             # 缺失身份证信息
                    this.showResult('verify')
                    tongji('withdraw_fill_IdCard_'+amountMap[amountType])
                } else if (resData.code === 3003) {//3003             # 今日已提现
                    this.showResult('limit')
                    tongji('withdraw_jinRiYiTiXian_'+amountMap[amountType])
                } else {
                    this.showResult('fail')
                    tongji('withdraw_fail_'+amountMap[amountType])
                }
                this.setState({
                    isWithdraw: true
                })
            })
    }


    selectType(type) {
        this.setState({amountType: type})
    }

    showResult(status) {
        this.setState({
            errorCode: status
        })
    }

    hideResult() {
        this.setState({
            errorCode: ''
        })
    }

    hideRegisterModel = () => {
        this.setState({
            isRegister: false
        })
    }

    render() {
        const {profitAll, errorCode, pageLoad, amountArray, amountType, isNewUser, isRegister} = this.state
        return (
            pageLoad ? <LoadingAnimationA/>
                : <div className="withdraw-wrapper">
                    <div className="withdrawCard">
                        <h6>可提现金额(元)</h6>
                        <div
                            className="money">{profitAll && profitAll.balance_amount > 0 ? profitAll.balance_amount : '0.00'}</div>
                        <div
                            className="unpay">提现中金额(元)：<span>{profitAll && profitAll.withdrawing_amount ? profitAll.withdrawing_amount : '0.00'}</span>
                        </div>
                        <div className="amountBox">
                            <p>请选择你要的提现金额：</p>
                            {
                                amountArray.map((item, index) => {
                                    return (
                                        profitAll && profitAll.balance_amount >= item.amount
                                            ? <div className="inner" key={index}>
                                                {
                                                    item.amount === 1 ?
                                                        isNewUser ?
                                                            <div className={"amountBtn disable frist"}>{item.amount}元</div>
                                                            :
                                                            <div className={amountType !== item.type ? "amountBtn frist" : "amountBtn frist select"}
                                                                 onClick={() => {this.selectType(item.type)}}>{item.amount}元
                                                            </div>
                                                        :
                                                        <div className={amountType !== item.type ? "amountBtn" : "amountBtn select"}
                                                             onClick={() => {this.selectType(item.type)}}>{item.amount}元
                                                        </div>
                                                }
                                            </div>
                                            :
                                            <div className="inner" key={index}>
                                                <div className={`amountBtn disable ${item.amount === 1 ? 'frist' : ''}`}>{item.amount}元</div>
                                            </div>
                                    )
                                })
                            }
                        </div>
                        {
                            this.state.isWithdraw ?
                                <div className={amountType !== -1 ? "withdrawBtn" : "withdrawBtn disable"}
                                     onClick={this.requestWithdraw}>
                                    确认提现
                                </div> :
                                <div className="withdrawBtn">
                                    <ButtonLoading text={'加载中'} color={'#fff'}/>
                                </div>

                        }
                    </div>
                    {/*提现说明*/}
                    <Notice/>
                    {/*提现累计超过800元需要绑定姓名与身份证号*/}
                    {
                        errorCode === 'verify'
                            ? <Certificate
                                    showResult={this.showResult}
                                    hide={this.hideResult}
                                    changeAmountData={this.changeAmountData}/>
                            : null
                    }
                    {/*提现结果modal*/}
                    {errorCode === 'success' || errorCode === 'fail' || errorCode === 'limit' || errorCode === 'choice' ?
                        <WithdrawResult errorCode={errorCode} hide={this.hideResult}/> : null}
                    {/*新用户先注册手机号*/}
                    {
                        isRegister ? <RegisterModal
                                            changeAmountData={this.changeAmountData}
                                            hideRegisterModel={this.hideRegisterModel} /> : null
                    }
                </div>
        )
    }
}
const Notice = () => {
    return <div className="notice">
        <h6>提现说明</h6>
        <p>1.关于提现金额和时间的说明如下：</p>
        <p> （1） 现支持提现到微信账户，首次仅1元即可提现；</p>
        <p> （2）提现成功后，我们将尽快完成审核并支付，预计1-3个工作日到账;</p>
        <p>2.若当月累计提现超过800元，根据《中华人民共和国个人所得税法》相关规定，需要提供相关身份信息，为你代扣缴个人所得税，感谢你的配合。</p>
    </div>
}