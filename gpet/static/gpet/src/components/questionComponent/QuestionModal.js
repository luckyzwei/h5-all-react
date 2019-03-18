import React,{Component} from 'react'

export default class QuestionModal extends Component {
    render(){
        const {hide} = this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox feedbackBox">
                    <div className="text">问题已反馈，我们将尽快处理，<br/>1个工作日后可尝试操作。</div>
                    <div className="butt" onClick={hide}>我知道啦！</div>
                </div>
            </div>
        )
    }
}