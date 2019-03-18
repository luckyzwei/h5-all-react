import React,{Component} from 'react'

const Success = ({onClick}) => {
    return (
        <div className="text">
            <h6>提现成功</h6>
            <p>收益将于1-3个工作日到达主人的微信钱包</p>
            <div className="butt" onClick={onClick}>知道啦！</div>
        </div>
    )
}

const Fail = ({onClick}) =>{
    return (
      <div>
        <div className="text">
            <p style={{lineHeight:'82px'}}>网络波动，请稍后重试!</p>
        </div>
        <div className="butt" onClick={onClick}>知道啦！</div>
    </div>
    )
}

const Limit = ({onClick}) => {
    return (
        <div>
          <div className="text">
              <p>你今天已经提过现了，<br/>请明天再来吧~</p>
          </div>
          <div className="butt" onClick={onClick}>知道啦！</div>
      </div>
      )
}

const Choice = ({onClick}) => {
    return (
        <div>
            <div className="text">
                <p>请选择你的提现金额~</p>
            </div>
            <div className="butt" onClick={onClick}>知道啦！</div>
        </div>
    )
}

export default class WithdrawResult extends Component {
    render(){
        const {hide,errorCode} = this.props
        let  view
        switch (errorCode) {
            case 'success':
                view = <Success onClick={hide}/>
                break;
            case 'fail':
                view = <Fail onClick={hide}/>
                break;
            case 'limit':
                view = <Limit onClick={hide}/>
                break;
            case 'choice':
                view = <Choice onClick={hide}/>
                break;
            default:
                break;
        }
        return (
            <div className="modalWrapper">
                <div className={errorCode==='success'?"modalBox resultBox success":"modalBox resultBox fail"}>
                    {view}
                </div>
            </div>
        )
    }
}
