import React, {Component} from 'react'
import NaviBar from '../shareComponent/Navibar/Index'
import GroupItem from './GroupItem'
import ChRobotName from './ChRobotName'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import LoadingAnimationB from '../shareComponent/LoadingAnimationB'
import {sendEvent, format_date} from '../../funStore/CommonFun'
import {tongji} from '../../constants/TrackEvent'
import {group_list, change_robot_name, task_range} from '../../funStore/CommonPort'
import {NoList} from '../shareComponent/notList'
import {history} from '../../index'
import './index.scss'

const loadingHeight = -80
export default class GroupList extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            pageLoad: false,
            startPos: 0,
            bottomDistance: 0,
            viewImport: false,
            type: 1, //1 已同步，2 待同步
            pageInfo: {
                current_page: 0,
                page_size: 20,
                total_page: 1
            },
            listData: [],
            checkItem: {},
            templateData: {
                '1': {
                    s: 1,
                    pageInfo: {
                        current_page: 0,
                        page_size: 20,
                        total_page: 1
                    },
                    listData: []
                },
                '2': {
                    s: 0,
                    pageInfo: {
                        current_page: 0,
                        page_size: 20,
                        total_page: 1
                    },
                    listData: []
                },
            },
            // delFlag: false,
            groupId: '',
            btnBlock: false,
            nav: [
                {text: '已同步', type: 1, num: '(0)'},
                {text: '待同步', type: 2, num: '(0)'}
            ],
            robot_name: '',
            changeName: false,
            sensitCheck: true,
            switchStatus:true
        }
        this.touchStartHandle = this.touchStartHandle.bind(this)
        this.touchMoveHandle = this.touchMoveHandle.bind(this)
        this.touchEndHandle = this.touchEndHandle.bind(this)
        this.pullList = this.pullList.bind(this)
        this.checkHandle = this.checkHandle.bind(this)
        this.changeNav = this.changeNav.bind(this)
        this.scrollLoad = this.scrollLoad.bind(this)
    }

    componentDidMount() {
        let self = this
        self.getGroupData()
    }

    getGroupData = () => {
        const {pageInfo} = this.state
        // 拉群初始化
        // /groups?status status 1 评星成功，0 等待评星
        const url_error = `current_page=0&page_size=${pageInfo.page_size}&status=1` //评星成功
        const url_run = `current_page=0&page_size=${pageInfo.page_size}&status=0` //等待评星
        let P2 = group_list(url_error)
        let P3 = group_list(url_run)
        Promise.all([P2, P3]).then((values) => {
            let {templateData, listData, pageInfo, type, nav} = this.state
            values.forEach((v, i) => {
                templateData[i + 1].pageInfo = v.page_info
                templateData[i + 1].listData = v.data !== null ? v.data.map(item => {
                    return {...item, expand: false}
                }) : []
                nav[i].num = ''
                nav[i].num = `${nav[i].num}(${v.page_info.total_records ? v.page_info.total_records : 0})`
            })
            pageInfo = templateData[type].pageInfo
            listData = templateData[type].listData
            this.setState({templateData, pageInfo, listData, type, nav, loading: false})
        })
    }

    touchStartHandle(e) {
        const {pageLoad} = this.state
        if (pageLoad) return
        const listEle = this.refs.wrapper
        let {scrollHeight, scrollTop, clientHeight} = listEle
        //记录触摸位置以及距离底部位置
        this.setState({
            startPos: e.touches[0].pageY,
            bottomDistance: scrollHeight - scrollTop - clientHeight
        })
    }

    touchMoveHandle(e) {
        const {startPos, bottomDistance, pageLoad, listData} = this.state
        if (pageLoad) return
        const listEle = this.refs.wrapper
        let {scrollHeight, scrollTop, clientHeight} = listEle
        // 当滚动到底部时触发
        if (scrollHeight === scrollTop + clientHeight && e.touches[0].pageY < startPos && listData.length > 0) {
            let distance = e.touches[0].pageY - startPos
            let offset = distance + bottomDistance
            // 最大上滑高度不超过设定值
            offset = offset < loadingHeight ? loadingHeight : offset
            this.refs.list.style.transform = "translateY(" + (offset) + "px)"
        }
    }

    touchEndHandle(e) {
        const {startPos, bottomDistance, pageLoad} = this.state
        if (pageLoad) return
        let distance = e.changedTouches[0].pageY - startPos
        let offset = distance + bottomDistance
        offset = offset < loadingHeight ? loadingHeight : offset
        // 到达最大高度加载，否则取消，返回原位置
        if (offset === loadingHeight) {
            if (!pageLoad) {
                this.setState({
                    pageLoad: true
                }, this.scrollLoad)
            }
        } else {
            // this.refs.list.style.transform = "translateY(0px)"
        }
    }

    pullList() {
        // 假拉列表
        setTimeout(() => {
            this.setState({
                pageLoad: false
            })
            this.refs.list.style.transform = "translateY(0px)"
        }, 500)
    }

    checkHandle(item) {
        this.setState({
            listData: this.state.listData.map(v => {
                return v.code === item.code ? {
                    ...v,
                    expand: !v.expand
                } : {
                    ...v,
                    expand: false
                }
            }),
            checkItem: item
        })
    }

    changeNav(nextType) {
        let {templateData, listData, pageInfo, type} = this.state
        templateData[type].pageInfo = pageInfo
        templateData[type].listData = listData
        type = nextType
        listData = templateData[nextType].listData
        pageInfo = templateData[nextType].pageInfo
        this.setState({templateData, listData, pageInfo, type})
        this.refs.wrapper.scrollTop = 0
    }

    scrollLoad() {
        const {pageInfo, type} = this.state
        if (pageInfo.current_page + 1 < pageInfo.total_page) {
            const url = `current_page=${pageInfo.current_page + 1}&page_size=${pageInfo.page_size}&status=${type === 1 ? 1 : 0}`
            group_list(url).then(res => {
                this.setState({
                    listData: this.state.listData.concat(res.data.map(item => {
                        return {
                            ...item,
                            expand: false
                        }
                    })),
                    pageInfo: res.page_info,
                    pageLoad: false
                })
                this.refs.list.style.transform = "translateY(0px)"
            })
        } else {
            this.pullList()
        }
    }

    toogleRobotName = (name) => {
        this.setState({
            robot_name: name,
            sensitCheck: true
        })
    }
    changeRobotName = (robot_name) => {
        const {checkItem, changeName} = this.state
        if (changeName) return
        this.setState({changeName: true})
        change_robot_name(`${checkItem.code}/robot_name`, {remark_name: robot_name}).then(resData => {
            if (resData.code === 1200) {
                this.toogleRobotName('')
                sendEvent("messages", {msg: "修改成功", status: 200})
                checkItem.robot_name = robot_name
                this.setState({
                    listData: this.state.listData.map(v => {
                        return v.code === checkItem.code ? {
                            ...v,
                            robot_name: robot_name
                        } : {...v}
                    }),
                    checkItem
                })

            } else if (resData.code === 2003) {
                this.chnageSensitCheck(false)
            } else {
                this.toogleRobotName('')
                sendEvent("messages", {msg: "修改失败", status: 200})
            }
            this.setState({changeName: false})
            tongji('grouplist_changeGroupName', robot_name)
        })
    }

    chnageSensitCheck = (state) => {
        this.setState({
            sensitCheck: state
        })
    }

    handleSwitch = (item) => {
        const {listData,switchStatus} = this.state
        if(!switchStatus) return
        // "rcv_task_flag": //0关闭1开启
        let parmas = [{code: item.code, rcv_task_flag: item.launch_switch === 0 ? 1 : 0}]
        this.setState({
            switchStatus:false
        })
        task_range(parmas).then(res => {
            if (res.code === 1200)
                this.setState({
                    listData: listData.map(v => {
                        return v.code === item.code ? {
                            ...v,
                            launch_switch: item.launch_switch === 0 ? 1 : 0
                        } : {...v}
                    }),
                    // switchStatus:true

                })
                setTimeout(()=>{
                    this.setState({
                        switchStatus:true
                    })
                },1000)
                tongji('grouplist_tuiWenSwitch',item.launch_switch === 0 ? 'open' : 'close')

        })

    }

    render() {
        const {loading, type, listData, pageLoad, checkItem, nav, robot_name} = this.state
        return (
            loading ? <LoadingAnimationA/>
                : <div className="group-wrapper">
                    <div className="inner" ref="wrapper"
                         onTouchStart={this.touchStartHandle}
                         onTouchMove={this.touchMoveHandle}
                         onTouchEnd={this.touchEndHandle}>
                        <div className="header" onClick={() => {
                            history.push('/grouppet/star');
                            tongji('grouplist_shuShiDu');
                        }}>
                            <div className="title"/>
                        </div>
                        <NaviBar nav={nav} changeNav={this.changeNav}/>
                        <ul ref="list" className='ulHeigth'>
                            {
                                listData && listData.length > 0 ? listData.map((item, index) => {
                                    return (
                                        type === 1
                                            ? <GroupItem key={index} item={item} expand={item.expand}
                                                         checkHandle={this.checkHandle}
                                                         showRobot={this.toogleRobotName}
                                                         handleSwitch={this.handleSwitch}
                                            />
                                            : <div className="groupItem groupItem-two" key={index}>
                                                <div className="cardHeader">
                                                    <div>
                                                        <span className="groupName">{item.name ? item.name : '未命名'}</span>
                                                        <span className='time'>{item.create_date?format_date(item.create_date, 'MM/DD'):''}</span>
                                                    </div>
                                                </div>
                                            </div>
                                    )

                                }) : <NoList type='GROUP_LIST'/>


                            }
                        </ul>
                    </div>
                    <div className="loadingBox">{listData && listData.length > 0 && pageLoad ?
                        <LoadingAnimationB/> : null}</div>
                    <div className="buttonBox">
                        <div className="importBtn saveBtn" onClick={() => {
                            history.push('/grouppet/import');
                            tongji('grouplist_clickLaQunBtn');
                        }}>拉群领红包
                        </div>
                    </div>
                    {
                        robot_name !== '' ? <ChRobotName
                            sensitCheck={this.state.sensitCheck}
                            checkItem={checkItem}
                            changeName={this.state.changeName}
                            sensitTrue={() => this.chnageSensitCheck(true)}
                            hideHandle={() => this.toogleRobotName('')}
                            confirmHandle={this.changeRobotName}/> : null
                    }
                </div>
        )
    }
}
