import React, {Component} from 'react'
import {sendEvent} from '../../funStore/CommonFun'
import PromptBox from '../shareComponent/PromptBox'
import NoKeyword from '../keyWordComponent/NoKeyword'
import {tongji} from '../../constants/TrackEvent'//埋点监测
import {Keywords_DELETE} from '../../funStore/CommonPort'
import KeyWItem from './KeyWItem'

export default class KeyWordMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            promptStatus: false,
            itemId: '',
            delStatue: true
        }

    }

    componentDidMount() {
        document.title = '关键词回复'
    }

    //open  modal
    handleOpen = (id) => {
        this.setState({
            promptStatus: true,
            itemId: id
        })
    }
    //close 撤回 modal
    handleClose = (e) => {
        e.stopPropagation()
        this.setState({
            promptStatus: false,
            itemId: ''
        })
    }
    //确定删除
    handleConfrim = (e) => {
        const _self = this;
        let ruleId = _self.state.itemId
        if (!this.state.delStatue) return
        this.setState({delStatue: false})
        let parmas = {id: ruleId}
        Keywords_DELETE(parmas).then(res => {
            if (res.code === 1200) {
                sendEvent("messages", {msg: "已删除", status: 200})
                tongji('keyWord_delete_success')
                _self.props.backTask(ruleId)
            } else {
                sendEvent("messages", {msg: "删除失败", status: 200})
                tongji('keyWord_delete_fail')
            }
            this.setState({delStatue: true})
            _self.handleClose(e);

        })
    }

    render() {
        const {promptStatus} = this.state
        const {keywordData, goDetails} = this.props
        return (
            keywordData && keywordData.length > 0 ?
                <div className='keyword-containter'>
                    <div className='keywordWrapper'>
                        <div className="header">
                            <div className='title-prompt'>*最多可以设置3个关键词回复</div>
                        </div>
                        <div className="content">
                            {
                                keywordData && keywordData.map((item, index) => {
                                    return <KeyWItem key={index} item={item}
                                                     handleOpen={this.handleOpen}
                                                     goDetails={goDetails}/>
                                })
                            }
                        </div>
                        {
                            keywordData.length < 3 ?
                                <div className='addKeyword active' onClick={() => goDetails('')}>新增关键词</div>
                                : <div className={`addKeyword`}>新增关键词</div>
                        }
                    </div>
                    {promptStatus ? <PromptBox text={'确认删除本条关键词?'} onClose={this.handleClose}
                                               onConfrim={(e) => this.handleConfrim(e)}/> : null}
                </div>
                : <NoKeyword history={this.props.history}/>

        )
    }
}
