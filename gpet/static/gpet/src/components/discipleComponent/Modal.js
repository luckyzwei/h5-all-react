import React,{Component} from 'react'

const Success = ({hide}) => {
    return (
        <div className="modalBox resultBox success">
            <div className="text">你的徒弟会更加努力哒！</div>
            <div className="butt" onClick={()=>{hide('')}}>知道啦！</div>
        </div>
    )
}

const Fail = ({hide}) => {
    return (
        <div className="modalBox resultBox fail">
            <div className="text">每天只能唤醒一次哦～</div>
            <div className="butt" onClick={()=>{hide('')}}>知道啦！</div>
        </div>
    )
}

export default class Modal extends Component {
    render(){
        const {modalFlag,showModal} = this.props
        let view 
        switch (modalFlag) {
            case 'success':
                view = <Success hide={showModal}/>;
                break;
            case 'fail':
                view = <Fail hide={showModal}/>;
                break;
            default:
                break;
        }
        return (
            <div className="modalWrapper">
                {view}
            </div>
        )
    }
}