import React, {Component} from 'react'
import {tongji} from '../../constants/TrackEvent'
import {disciple_wake} from '../../funStore/CommonPort'
import {format_date} from '../../funStore/CommonFun'

export default class DiscipleItem extends Component {
    constructor(props) {
        super(props)
        this.state = {
            maxHeight: 0,
            minHeight: 0,
            remindFlag: true,
            buttonBlock: false
        }
        this.expandHandle = this.expandHandle.bind(this)
        this.remindHandle = this.remindHandle.bind(this)
    }

    componentDidMount() {
        this.setState({
            maxHeight: this.refs.cardHeader.offsetHeight + this.refs.cardDetail.offsetHeight,
            minHeight: this.refs.cardHeader.offsetHeight
        })
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.item.user_id !== this.props.item.user_id) {
            this.setState({
                maxHeight: this.refs.cardHeader.offsetHeight + this.refs.cardDetail.offsetHeight,
                minHeight: this.refs.cardHeader.offsetHeight
            })
        }
    }

    expandHandle(e) {
        e.stopPropagation()
        this.props.checkHandle(this.props.index)
    }

    remindHandle(e) {
        let self = this
        const {item} = this.props
        let parmas = {
            is_import: item.is_import,
            is_apprentice: item.is_apprentice,
            user_id: item.user_id
        }
        if (this.state.buttonBlock) return
        this.setState({
            buttonBlock: true
        })
        disciple_wake(parmas).then(resData => {
            self.setState({
                buttonBlock: false
            })
            if (resData.code === 1200) {
                this.props.showModal('success')
                self.setState({
                    remindFlag: false
                })
            } else {
                this.props.showModal('fail')
            }
        })
        tongji('disciple_huanXingTuDi')
    }

    render() {
        const {remindFlag, maxHeight, minHeight} = this.state
        const {index, checkIndex, item} = this.props
        // "is_import":boolean ,         //是否导群true已导群
        //     "is_apprentice":booleanm,	   //是否收徒,true已收徒
        return (
            <li ref="content" style={{height: item.isExpand && checkIndex === index ? maxHeight + 'px' : minHeight + 'px'}}>
                <div className="detail" ref='cardHeader' onClick={this.expandHandle}>
                    <div className="groupName">{item.name ? item.name : '待同步'}</div>
                    <div className="time">{format_date(item.create_date, 'YYYY/MM/DD')}</div>
                    <span className={item.isExpand && checkIndex === index ? "downArrow up" : "downArrow"}/>
                </div>
                <div ref="cardDetail" className="operateBox">
                    <div className="tag">
                        <span className={item.is_import ? '' : "disable"}>{item.is_import ? '已导群' : "未导群"}</span>
                        <span
                            className={item.is_apprentice ? '' : "disable"}>{item.is_apprentice ? '已收徒' : "未收徒"}</span>
                    </div>
                    {
                        remindFlag && item.is_remind === 1
                            ? <div className="callbackBtn" onClick={this.remindHandle}>唤醒徒弟</div>
                            : <div className="callbackBtn disable">唤醒徒弟</div>

                    }
                </div>
            </li>
        )
    }
}