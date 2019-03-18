import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import MsgEmpty from '../shareComponent/MsgEmpty'
import Message from '../shareComponent/Message'
import {sendEvent} from '../../funStore/CommonFun'
import {tongji} from '../../constants/TrackEvent'
import {OwnerIsGroup, get_welcome_list, save_welcome} from "../../funStore/CommonPort";

export default class CreateWelmsg extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasGroup: true,
            params: {
                id: '',
                name: '',
                welcome_msg: '',
            },
            groupList: [],
            clearStatus: false,
            changeId: '',
            changeStatus: false

        }
    }

    componentDidMount() {
        document.title = '入群欢迎语'
        //1.判断用户是否有群主群
        let self = this
        OwnerIsGroup().then(res => {
            if (res.code === 1200 && res.data) {
                self.getWelcomemsgData()
            } else {
                self.setState({
                    isHasGroup: false,
                    loading: false
                })
            }
        })
    }

    // 获取群宠群主群群欢迎语列
    getWelcomemsgData = () => {
        //调取接口
        get_welcome_list().then(resData => {
            this.setState({loading: false})
            if (resData.code === 1200) {
                this.setState({
                    groupList: resData.data,
                })
            }

        })
    }
    handleTextarea = (e, id) => {
        let msg = e.target.value
        this.changeGroupList(id, msg)
    }

    handleSaveWelcom = (id, typeFlag) => {
        const {groupList, params, changeStatus} = this.state
        let self = this
        if (typeFlag === 1) {//做了修改 保存
            if (changeStatus) return
            this.setState({changeStatus: true})
            groupList.forEach(item => {
                if (item.id === id) {
                    params.id = id
                    params.welcome_msg = item.welcome_msg
                    self.setState({
                        params
                    }, () => {
                        self.handleSave(this.state.params)

                    })
                    return
                }
            })
        }
    }

    handleSave = (params) => {
        save_welcome(params.id + '/welcome', {welcome_msg: params.welcome_msg}).then(resData => {
            if (resData.code === 1200) {
                sendEvent("messages", {msg: "保存成功", status: 200});
            } else if (resData.code === 2003) {
                sendEvent("messages", {msg: "内容不符合安全标准", status: 201})
            } else {
                sendEvent("messages", {msg: "保存失败", status: 201})
            }
            this.setState({
                changeStatus: false
            })
        })
        tongji('welcome_click_saveBtn')
    }
    changeGroupList = (id, msg) => {
        this.setState({
            groupList: this.state.groupList.map(item => {
                return (
                    item.id === id ? {
                        ...item,
                        welcome_msg: msg,
                        typeFlag: 1
                    } : {...item}
                )
            })
        })
    }

    showHandle = (id) => {
        this.setState({
            clearStatus: true,
            changeId: id
        })
    }

    render() {
        const {loading, isHasGroup, groupList, clearStatus, changeId, changeStatus} = this.state
        return (
            loading ?
                <LoadingAnimationA/>
                :
                isHasGroup ?
                    <div className='new-welcomeView'>
                        <div className="header">
                            <div className="title"/>
                        </div>
                        <div className='welcomeList'>
                            {
                                groupList.map((item, index) =>
                                    <div className='listItem' key={index}>
                                        <div className='groupname'>
                                            {item.name}
                                        </div>
                                        <div className='cm-textarea groupWelcome'>
                                            <textarea name="welcomeMsg" placeholder='输入入群欢迎语'
                                                      value={item.welcome_msg != null && item.welcome_msg !== undefined ? item.welcome_msg : ''}
                                                      onFocus={() => this.showHandle(item.id)}
                                                      onBlur={() => {window.scroll(0, 0)}}
                                                      onChange={(e) => this.handleTextarea(e, item.id)}
                                                      maxLength={280}
                                            />
                                            {changeId === item.id?<Message/>:''}
                                        </div>
                                        <div className='welcomeSave'>
                                            <div className='wordlimit'>
                                                {item.welcome_msg != null ? item.welcome_msg.length<=200?item.welcome_msg.length:200 : 0}/200
                                            </div>
                                            <div>
                                                {
                                                    clearStatus && changeId === item.id ?
                                                        <button className='btnSave clearbtn'
                                                                onTouchEnd={() => {
                                                                    this.changeGroupList(item.id, '')
                                                                }}>清空</button> : null
                                                }
                                                <button className='btnSave'
                                                        onTouchEnd={!changeStatus ? () => this.handleSaveWelcom(item.id, item.typeFlag) : null}>保存
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )
                            }
                        </div>
                    </div>
                    :
                    <MsgEmpty type={3}/>

        )
    }
}
