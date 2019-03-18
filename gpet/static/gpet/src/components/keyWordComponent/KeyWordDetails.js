import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {sendEvent} from '../../funStore/CommonFun'
import AddMessGroup from '../messMsgComponent/AddMessGroup'
import AddKeyWord from './AddKeyWord'
import { tongji} from '../../constants/TrackEvent'
import ButtonLoading from '../shareComponent/ButtonLoading'
import {OwnerGroupList} from '../../funStore/CommonPort'

import {Keywords_data_list, Keywords_EDIT} from '../../funStore/CommonPort'

export default class KeyWordDetails extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasMsg: true,//是否有群发任务 false 没有 true有
            isHasGroup: true,//是否有导群
            isSelectGroup: false,
            groupList: [],
            params: {
                group_codes: [],
                keywords: [],
                reply_content: ''
            },
            btnColor: false,
            saveState: true,
        }
    }

    componentDidMount() {
        document.title = '关键词回复'
        let self = this
        let id = this.props.match.params.id
        this.getOwnerGroups()
        //编辑
        if (id !== undefined) {
            Keywords_data_list('/' + id).then(res => {
                if (res.code === 1200) {
                    self.setState({
                        params: res.data
                    }, this.btnChange)
                }
                self.setState({loading: false})
            })
        }
    }

    //查询用户的群主群列表
    getOwnerGroups = () => {
        const _self = this;
        OwnerGroupList(0, -1).then(res => {
            this.setState({loading: false})
            if (res.code === 1200) {
                _self.setState({
                    groupList: res.data
                })
            }
        })
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

    setHandleParams = (task, type) => {
        const {params} = this.state
        if (type === 0) {
            params.group_codes = task
        } else {
            params.keywords = params.keywords.concat(task)
        }
        this.setState({
            params,
            isSelectGroup: false
        }, this.btnChange)
    }

    handleTextarea = (e) => {
        const {params} = this.state
        params.reply_content = e.target.value
        this.setState({
            params
        }, this.btnChange)
    }

    btnChange = () => {
        this.setState({
            btnColor: this.verifyHandle()
        })
    }

    verifyHandle = () => {
        const {params} = this.state
        let flag = true
        if (params.keywords.length === 0 || params.group_codes.length === 0 || params.reply_content === '') {
            flag = false
        }
        return flag
    }

    deleteKeyword = (data, index, e) => {
        e.stopPropagation()
        const {params} = this.state
        params.keywords.splice(index, 1)
        this.setState({
            params
        }, this.btnChange)
    }

    saveHandel = () => {
        const {params, saveState} = this.state
        if (saveState) {
            this.setState({
                saveState: false
            })

            let id = this.props.match.params.id
            if (id !== undefined) {
                this.requestList(params, 'PUT');
            } else {
                this.requestList(params, 'POST') //新增
            }
        }

    }

    requestList = (params, type) => {
        Keywords_EDIT(params, type).then(resData => {
            if (resData.code === 1200) {
                this.props.getKeywordData()
                sendEvent("messages", {msg: type === 'POST' ? "新增成功" : '修改成功', status: 200, timer: 1000})
                setTimeout(() => {
                    this.props.history.push('/grouppet/keyword/keywordlist')
                }, 1500)
            } else if (resData.code === 1403) { //参数错误
                sendEvent("messages", {msg: resData.description, status: 201})
            } else if (resData.code === 2003) {
                sendEvent("messages", {msg: "内容不符合安全标准", status: 201})
            } else {
                sendEvent("messages", {msg: type === 'POST' ? "新增失败" : '修改失败', status: 201})
            }
            this.setState({
                saveState: true
            })
            tongji('keyWord_click_save')
        })
    }

    render() {
        const {loading, isSelectGroup, groupList, params, btnColor, saveState} = this.state
        return (
            loading ? <LoadingAnimationA/> :
                <div className='keyword-containter'>
                    <div className='keywordDetails createMsg-wrapper'>
                        <div className="header"/>
                        <div className="content">
                            <AddKeyWord keywords={params.keywords} setHandleParams={this.setHandleParams}
                                        deleteKeyword={this.deleteKeyword}/>
                            <div className='cm-changeBox' onTouchEnd={(e) => this.chooseGroup(e)}>
                                {
                                    params.group_codes.length > 0
                                        ? <div className='left selected'>{params.group_codes.length}个群</div>
                                        : <div className='left'>选择群</div>
                                }
                                <div className='right'/>
                            </div>
                            <div className='cm-textarea'>
                            <textarea name="title" placeholder='输入自动回复的内容'
                                      value={params.reply_content} maxLength={280}
                                      onChange={(e) => this.handleTextarea(e)}
                                      onBlur={() => {
                                          window.scroll(0, 0)
                                      }}/>
                                <div
                                    className='wordlimit'>{params.reply_content.length <= 200 ? params.reply_content.length : 200}/200
                                </div>
                            </div>
                            <div className='prompt'>注：关键词只有在@小宠的情况下才会触发，所有关键词都是模糊匹配</div>
                        </div>
                        {
                            saveState ? <div className={`addKeyword ${btnColor ? 'active' : ''}`}
                                             onClick={btnColor ? this.saveHandel : null}>保存</div>
                                : <div className={`addKeyword ${btnColor ? 'active' : ''}`}><ButtonLoading text={'保存中'}
                                                                                                           color={'#fff'}/>
                                </div>
                        }
                    </div>
                    {
                        isSelectGroup ? <AddMessGroup groupList={groupList} paramsSelected={params.group_codes}
                                                      setHandleParams={this.setHandleParams}
                                                      closeSelectGroup={this.closeSelectGroup}/> : null
                    }
                </div>
        )
    }
}
