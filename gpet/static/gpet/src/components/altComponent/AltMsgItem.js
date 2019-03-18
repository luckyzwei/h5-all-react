import React, {Component} from 'react'
import AnswerBox from './AnswerBox'

export default class AltMsgItem extends Component {
    constructor(props) {
        super(props)
        this.state = {
            status: this.props.message.status,
        }
    }

    readHandle = (item) => {
        this.props.expandHandle(item)
        this.setState({status: 1})
    }

    render() {
        const {status} = this.state
        const {message, selectMessage, expandHandle, selectId, showPreviewImg} = this.props
        return (
            <div className="msgItemOuter">
                <div className="msgItem" ref='msgItem'>
                    <div className={status === 0 ? "msgInfo" : "msgInfo read"} onClick={() => {this.readHandle(message)}}>
                        <div className="bar"/>
                        <div className='left'>
                            <div className='groupName'>{message.group_name}</div>
                            <div className="info">
                                <div className="msg textHide"><span>[有人@我] </span>{message.msg_content}</div>
                            </div>
                        </div>
                        <div className='right'>
                            <span
                                className={`unexpand ${selectMessage.isExpand && message.msg_id === selectId ? 'expand' : ''}`}>
                                {selectMessage.isExpand && message.msg_id === selectId ? '收起' : '展开'}
                            </span>
                        </div>
                    </div>
                </div>
                {
                    selectMessage && selectMessage.isExpand && message.msg_id === selectId
                        ? <AnswerBox message={selectMessage} expandHandle={expandHandle} showPreviewImg={showPreviewImg}/>
                        : null
                }
            </div>
        )
    }
}