import React, {Component} from 'react'
import DatePickerBox from '../shareComponent/datepicker/DatePickerBox';
import {ErrorNoNews} from '../shareComponent/ErrorMessage'
import AddMessGroup from './AddMessGroup'
import {formatDate, format_date, sendEvent, getQueryString} from '../../funStore/CommonFun'
import MsgEmpty from '../shareComponent/MsgEmpty'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {tongji} from '../../constants/TrackEvent'
import {OwnerGroupList, get_create_msg_list, create_mass_msg} from "../../funStore/CommonPort";
import ButtonLoading from '../shareComponent/ButtonLoading'
export default class CreateMessMsg extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isCreate: true,
            params: {
                "message": {
                    "type": 3,             // 消息类型
                    "content": '',           // 内容
                    "title": '',             // 标题
                    "desc": '',              // 描述
                    "url": '',              // 链接
                },
                "group_ids": [],            // 群ids
                "send_date": ''               // YYYY-MM-DD
            },
            groupList: [],
            isSelectGroup: false,
            isOpen: false,
            btnDisabled: false,
            btnColor: false,
            placeholder: false
        }

    }

    componentDidMount() {
        document.title = '新建群发'
        this.hasMaterial()
    }

    //判断是否有素材可创建
    // 创建成功 之后  失效群发素材
    hasMaterial = () => {
        let self = this
        let task_id = getQueryString('task_id')
        get_create_msg_list(task_id).then(res => {
            if (res.code === 1200) {
                //有素材 获取群主群列表
                self.getOwnerGroups()
            } else {
                //没有素材
                self.setState({
                    isCreate: false,
                    loading: false,
                })
            }
        })

    }



    //查询用户的群主群列表
    getOwnerGroups = () => {
        //查询用户的群主群列表
        let _self = this;
        OwnerGroupList(0, -1).then(res => {
            this.setState({loading: false})
            if (res.code === 1200) {
                _self.setState({
                    groupList: res.data
                })
            }
        })
    }

    handleTextarea = (e) => {
        this.setState({
            placeholder: e.target.value === ''?false:true
        })
        const {params} = this.state
        params.message.content = e.target.value
        this.setState({params})
    }

    setHandleParams = (task, type) => {
        const {params} = this.state
        if (type === 0) {
            params.group_ids = task;
            this.setState({isSelectGroup: false})
        } else if (type === 1) {
            if (new Date(task).getTime() < new Date().getTime()) {
                sendEvent("messages", {msg: "创建时间选错啦", status: 200})
                return
            }
            params.send_date = formatDate(task, 'yyyy/mm/dd hh:mm')
            this.setState({
                isOpen: false
            })
        }
        this.setState({
            params
        }, this.btnChange)
    }

    chooseGroup = (e) => {
        e.preventDefault()
        this.setState({
            isSelectGroup: true
        })
    }

    closeSelectGroup = () => {
        this.setState({
            isSelectGroup: false,
        })
    }
    chooseTime = (e) => {
        e.stopPropagation();
        this.setState({isOpen: true})
    }

    handleCancel = (e) => {
        if (e.target.className === 'datepicker-modal') {
            document.querySelector('body').removeEventListener('click', this.handleCancel)
            this.setState({isOpen: false})
        }
    }
    verifyHandle = () => {
        const {params} = this.state
        var flag = true
        if (params.group_ids.length === 0 || params.send_date === '' || new Date(params.send_date).getTime() < new Date().getTime()) {
            flag = false
        }
        return flag
    }

    btnChange = () => {
        this.setState({
            btnColor: this.verifyHandle()
        })
    }

    handleConfirmCreate = () => {
        let self = this
        if (!self.verifyHandle()) return
        const {params} = this.state
        let task_id = getQueryString('task_id')
        let paramsData = {
            ...params,
            send_date: format_date(params.send_date, 'YYYY-MM-DD HH:MM') + ':00'
        }
        this.setState({btnDisabled: true})
        create_mass_msg(task_id, paramsData).then(res => {
            switch (res.code) {
                case 1200:
                    //创建成功跳转列表页
                    sendEvent("messages", {msg: "创建群发成功", status: 200})
                    setTimeout(() => {
                        self.props.history.push('/grouppet/messmsg')
                    }, 2000)
                    break;
                case 2003:
                    sendEvent("messages", {msg: "内容不符合安全标准", status: 201})
                    break;
                case 1404:
                    sendEvent("messages", {msg: "素材已失效", status: 201})
                    break;
                case 2004:
                    sendEvent("messages", {msg: "创建次数已用完", status: 201})
                    break;
                case 2005:
                    sendEvent("messages", {msg: "存在任务冲突", status: 201})
                    break;
                default:
                    sendEvent("messages", {msg: "创建群发失败", status: 201})
                    break;

            }
            this.setState({btnDisabled: false})
            tongji('CreateMessMsg_clickCreateBtn')
        })
    }

    render() {
        const {loading, isCreate, params, groupList, isSelectGroup, isOpen, btnColor, btnDisabled, placeholder} = this.state
        return (
            loading ? <LoadingAnimationA/>
                :
                <div className='new-containter'>
                    {
                        isCreate ?
                            groupList !== 'null' && groupList !== null && groupList.length > 0 ?
                                <div className='createMsg-wrapper'>
                                    <div className='cm-textarea'>
                                        <div className="textarea-placeholder">
                                        <textarea name="title" maxLength={280}
                                                  className={placeholder && params.message.content.length > 0 ? 'data-edits' : null}
                                                  onChange={(e) => this.handleTextarea(e)}
                                                  onBlur={() => {window.scroll(0, 0)}}
                                        />
                                        {placeholder && params.message.content.length > 0 ? null : <div className='fakePlaceholder'>输入配套文案(选填)<br/>添加配套文案可以使你的内容更有吸引力</div>}
                                        </div>
                                        <div className='wordlimit'>{params.message.content.length<=200?params.message.content.length:200}/200</div>
                                    </div>
                                    <div className='cm-changeBox' onClick={(e) => this.chooseGroup(e)}>
                                        {
                                            params.group_ids.length > 0
                                                ? <div className='left selected'>{params.group_ids.length}个群</div>
                                                : <div className='left'>选择群</div>
                                        }
                                        <div className='right'/>
                                    </div>
                                    <div className='cm-changeBox' onClick={this.chooseTime}>
                                        {
                                            params.send_date !== '' ?
                                                <div className='left selected'>{params.send_date}</div> :
                                                <div className='left'>选择时间</div>
                                        }

                                        <div className='right'/>
                                    </div>
                                    <div className='cm-btnBox'>
                                        <div className="button-view">
                                            {
                                                btnDisabled?
                                                    <button className='buttonNoSelect buttonSelected'>
                                                        <ButtonLoading text={'创建中'} color='#fff'/>
                                                    </button>
                                                    :
                                                    <button className={`buttonNoSelect ${btnColor ? 'buttonSelected' : ''}`}
                                                            onClick={this.handleConfirmCreate}>
                                                        确认创建
                                                    </button>
                                            }
                                        </div>
                                    </div>
                                </div>
                                :
                                <MsgEmpty type={4}/>
                            :
                            <ErrorNoNews type={5}/>
                    }

                    {
                        isSelectGroup ? <AddMessGroup groupList={groupList} paramsSelected={params.group_ids}
                                                      setHandleParams={this.setHandleParams}
                                                      closeSelectGroup={this.closeSelectGroup}/> : null
                    }
                    {
                        isOpen ? <DatePickerBox selectedTime={params.send_date} handleSelected={this.setHandleParams}
                                                handleCancel={this.handleCancel}/> : null
                    }
                </div>
        )
    }
}
