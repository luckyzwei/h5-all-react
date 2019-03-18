import React,{Component} from 'react'
import {tongji} from '../../constants/TrackEvent'
import {sendEvent} from '../../funStore/CommonFun'
import {fill_IdCard} from '../../funStore/CommonPort'
import Message from '../shareComponent/Message'

const ErrorTip = ({text,error}) => {
    return <div className="errorTip" style={{visibility:error?'visible':'hidden'}}>{text}</div>
}

export default class Certificate extends Component {
    constructor(props){
        super(props)
        this.state = {
            idError: false,
            nameError: false
        }
        this.requestWithdraw = this.requestWithdraw.bind(this)
    }
    requestWithdraw(){
        let params = {
            id_number: this.refs.id_number.value,
            name: this.refs.name.value
        }
        this.setState({
            idError: false,
            nameError: false
        })
        if(params.name===''){
            this.setState({
                nameError: true
            })
            return
        }
        if(params.id_number===''||(params.id_number.length!==15&&params.id_number.length!==18)){
            this.setState({
                idError: true
            })
            return
        }

        //补全身份证
        fill_IdCard(params).then(resData=>{
            if(resData.code===1200){
                sendEvent("messages",{msg:"提交成功",status:200})
                setTimeout(()=>{
                    this.props.changeAmountData()
                },2500)
            }else{
                sendEvent("messages",{msg:"提交失败",status:200})
                setTimeout(()=>{
                    this.props.hide()
                },2500)
            }
            tongji('tiXian_fill_IdCard')
        })
        tongji('tiXian_fill_IdCard')
    }
    render(){
        const {idError,nameError} = this.state
        return (
            <div className="modalWrapper">
                <div className="modalBox certificate">
                    <input type="text" className="name" placeholder="请输入你的姓名" ref="name" autoComplete="off"/>
                    <ErrorTip text={'请输入姓名'} error={nameError}/>
                    <input type="text" className="identify" placeholder="请输入你的身份证号" ref="id_number" autoComplete="off"/>
                    <ErrorTip text={'请输入正确身份证号'} error={idError}/>
                    <div className="confirmBtn" onClick={this.requestWithdraw}>确认</div>
                    <p className="noticeText">*当月提现超过800元需要绑定姓名与身份证号</p>
                    <div className="icon-cross closeBtn" onClick={this.props.hide}/>
                </div>
                <Message/>
            </div>
        )
    }
}