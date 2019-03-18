import React, {Component} from 'react'
import NaviBar from '../shareComponent/Navibar/Index'
import PromptBox from '../shareComponent/PromptBox'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import LoadingAnimationB from '../shareComponent/LoadingAnimationB'
import MsgEmpty from '../shareComponent/MsgEmpty'
import {sendEvent,format_date} from "../../funStore/CommonFun";
import {ErrorNoNews} from '../shareComponent/ErrorMessage'
import {tongji} from '../../constants/TrackEvent'
import {OwnerIsGroup,get_mass_msg_list,delete_mass_msg} from "../../funStore/CommonPort";

const loadingHeight = -80;
export default class MessMsgList extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasMsg: true,//是否有群发任务 false 没有 true有
            isHasGroup: true,//是否有导群
            pageLoad: false,
            startPos: 0,
            bottomDistance: 0,
            promptStatus: false,
            nav: [
                {text: '未来3天', type: 1,num:'(0)'},
                {text: '过去3天', type: 2,num:'(0)'}
            ],
            navType: 1,
            templateData: {
                '1': {
                    pageInfo: {
                        current_page:0,
                        page_size:20,
                        total_page:0,
                        total_records:0
                    },
                    listData: []
                },
                '2': {
                    pageInfo: {
                        current_page:0,
                        page_size:20,
                        total_page:0,
                        total_records:0
                    },
                    listData: []
                }
            },
            pageInfo: {
                current_page:0,
                page_size:20,
                total_page:0,
                total_records:0
            },
            listData: [],
            taskId: ''

        }
    }

    componentDidMount() {
        document.title = '群发消息'
        let self = this
        OwnerIsGroup().then(res=>{
            if(res.code===1200&&res.data){
                self.getTaskList()
            }else{
                self.setState({
                    isHasGroup:false,
                    loading:false
                })
            }
        })
    }

    getTaskList = () => {
        // up 未来一周 down 过去一周
        let P1 = get_mass_msg_list('up')
        let P2 = get_mass_msg_list('down')
        Promise.all([P1,P2]).then((values) => {
            let {nav,templateData, listData, pageInfo, navType} = this.state
            if((values[0].data&&values[0].data.length>0) ||(values[1].data&&values[1].data.length>0)){
                values.forEach((v, i) => {
                    templateData[i + 1].pageInfo = v.page_info
                    templateData[i + 1].listData = v.data!==null?v.data:[]
                    nav[i].num = ''
                    nav[i].num = `${nav[i].num}(${v.page_info.total_records ? v.page_info.total_records : 0})`
                })
                pageInfo = templateData[navType].pageInfo
                listData = templateData[navType].listData
                this.setState({templateData, pageInfo, listData, navType,loading: false})
            }else {
                this.setState({
                    loading: false,
                    isHasMsg: false //没有群发任务
                })
            }

        }).catch(err => {
            console.log(err)
        })
    }

    scrollLoad = () => {
        const {pageInfo, navType} = this.state
        if (pageInfo.currentPage + 1 < pageInfo.totalPage) {
            let url= `${navType===1?'up':'down'}`;
            get_mass_msg_list(url).then(res => {
                this.setState({
                    listData: this.state.listData.concat(res.data),
                    pageInfo: res.page_info,
                    pageLoad: false
                })
                this.refs.list.style.transition = "all 0.2s ease-in-out"
                this.refs.list.style.transform = "translateY(0px)"
            }).catch(err => {
                console.log(err)
            })
        } else {
            this.pullList()
        }
    }

    pullList() {
        // 假拉列表
        setTimeout(() => {
            this.setState({
                pageLoad: false
            })
            this.refs.list.style.transition = "all 0.2s ease-in-out"
            this.refs.list.style.transform = "translateY(0px)"
        }, 500)
    }


    //nav 切换 数据改变
    changeNav = (nextType) => {
        let {templateData, listData, pageInfo, navType} = this.state
        templateData[navType].pageInfo = pageInfo
        templateData[navType].listData = listData
        navType = nextType
        listData = templateData[nextType].listData
        pageInfo = templateData[nextType].pageInfo
        this.setState({templateData, listData, pageInfo, navType})
        this.refs.wrapper.scrollTop = 0
    }

    //open 撤回 modal
    handleOpen = (e, id) => {
        e.stopPropagation();
        this.setState({
            promptStatus: true,
            taskId: id
        })
    }
    //close 撤回 modal
    handleClose = (e) => {
        e.stopPropagation();
        this.setState({
            promptStatus: false,
            taskId: ''
        })
    }
    //确定撤回
    handleConfrim = (e) => {
        //   确定之后的操作 //撤销任务
        const _self = this;
        let {taskId} = _self.state;
        delete_mass_msg(taskId).then(res => {
            if (res.code === 1200) {
                sendEvent("messages", {msg: "已撤回", status: 200})
                _self.backTask(taskId)
            } else {
                sendEvent("messages", {msg: "撤回失败", status: 200})
            }
            _self.handleClose(e);
            tongji('messmsg_confirmRetract')
        });

    }

    backTask(id) {
        this.setState({
            listData: this.state.listData.filter(item => item.id !== id)
        },this.getTaskList)
    }

    touchStartHandle = (e) => {
        const {pageLoad} = this.state
        if (pageLoad) return
        const listEle = this.refs.wrapper
        let {scrollHeight, scrollTop, clientHeight} = listEle
        //记录触摸位置以及距离底部位置
        this.setState({
            startPos: e.touches[0].pageY,
            bottomDistance: scrollHeight - scrollTop - clientHeight
        })
        this.refs.list.style.transition = "none"
    }
    touchMoveHandle = (e) => {
        const {startPos, bottomDistance, pageLoad} = this.state
        if (pageLoad) return
        const listEle = this.refs.wrapper
        let {scrollHeight, scrollTop, clientHeight} = listEle
        // 当滚动到底部时触发
        if (scrollHeight === scrollTop + clientHeight && e.touches[0].pageY < startPos) {
            let distance = e.touches[0].pageY - startPos
            let offset = distance + bottomDistance
            // 最大上滑高度不超过设定值
            offset = offset < loadingHeight ? loadingHeight : offset
            this.refs.list.style.transform = "translateY(" + (offset) + "px)"
        }
    }
    touchEndHandle = (e) => {
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
                },this.scrollLoad)
            }
        } else {
            this.refs.list.style.transition = "all 0.2s ease-in-out"
            this.refs.list.style.transform = "translateY(0px)"
        }
    }

    goMsgContent = (id) => {
        this.props.history.push('/grouppet/messmsgetails/' + id)
        tongji('messmsg_goDetails')
    }

    render() {
        const {loading, pageLoad, isHasGroup, isHasMsg, nav, listData, promptStatus} = this.state
        return (
            loading ? <LoadingAnimationA/>
                :
                isHasGroup ?
                    isHasMsg ?
                        <div className='new-messMsgList'>
                            <div ref='wrapper'
                                 onTouchStart={this.touchStartHandle}
                                 onTouchMove={this.touchMoveHandle}
                                 onTouchEnd={this.touchEndHandle}>
                                <div className="header">
                                    <div className="title"/>
                                </div>
                                <NaviBar nav={nav} changeNav={this.changeNav}/>
                                <div className="messList" ref="list">
                                    {
                                        listData.map((item, index) =>
                                            <div className="cardBox" key={index} onClick={() => this.goMsgContent(item.id)}>
                                                <div className="item">
                                                    <span className='createDate'>群发消息 {format_date(item.send_date,'MM/DD HH:MM')}</span>
                                                    <div>
                                                        <span className="num">总计{item.group_counts}个群</span>
                                                        {
                                                            // 状态 0 待发送 1 已发送 2 发送失败
                                                            item.status === 2 ? <span className='msgtype msgWait'>发送失败</span>
                                                                :item.status === 0? <span className='msgtype msgWait'>待发送</span>
                                                                : <span className='msgtype msgAlready'>已发送</span>
                                                        }

                                                    </div>
                                                </div>
                                                <div className="item">
                                                    <span className="jumpArrow"/>
                                                    {
                                                        item.status === 0 ? <div className="withdrawBtn" onTouchEnd={(e) => this.handleOpen(e, item.id)}>撤回</div> :null
                                                    }
                                                </div>
                                            </div>
                                        )
                                    }
                                </div>
                            </div>
                            <div className="pageFooterLoad">{listData && pageLoad ? <LoadingAnimationB/> : null}</div>
                            {promptStatus ? <PromptBox text={'确认撤回本条群发?'} onClose={this.handleClose} onConfrim={this.handleConfrim}/> : null}
                        </div>

                        : <ErrorNoNews type={4}/>
                    : <MsgEmpty type={4}/>
        )
    }
}
