import React,{Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import TaskList from './TaskList'
import LoadingAnimationB from '../shareComponent/LoadingAnimationB'
import {tongji} from '../../constants/TrackEvent'
import {task_history_list} from '../../funStore/CommonPort'
import {NoList} from '../shareComponent/notList'
import {TaskDescrip} from '../shareComponent/modalDescrip/ModalDescrip'
import './index.scss'

const loadingHeight = -80;
export default class TaskMain extends Component {
    constructor(props){
        super(props)
        this.state={
            loading:true,
            pageLoad:false,
            startPos: 0,
            bottomDistance: 0,
            // current_page,page_size,total_page,total_records
            pageInfo: {
                current_page: 0,
                page_size: 20,
                total_page: 1
            },
            listData: [],
            taskId: '',
            modal:false
        }
    }
    componentDidMount(){
        document.title = '文章推送';
        this.getTaskList()
    }

    getTaskList=()=>{
        let {pageInfo,listData} =this.state
        //url1 :获取今日投放数据 url2 :获取过去3天投放数据
        const url = `current_page=${pageInfo.current_page}&page_size=${pageInfo.page_size}`
        task_history_list(url).then(res=>{
            listData = res.data
            pageInfo=res.page_info
            this.setState({ pageInfo, listData,loading:false})
        })
    }

    scrollLoad=()=>{
        let {pageInfo} = this.state
        if (pageInfo.current_page + 1 < pageInfo.total_page) {
            const url = `current_page=${pageInfo.current_page+1}&page_size=${pageInfo.page_size}`
            task_history_list(url).then(res=>{
                this.setState({
                    listData: this.state.listData.concat(res.data),
                    pageInfo: res.page_info,
                    pageLoad: false
                })
                this.refs.list.style.transition = "all 0.2s ease-in-out"
                this.refs.list.style.transform = "translateY(0px)"
            })

        } else{
            // 假拉列表
            setTimeout(() => {
                this.setState({
                    pageLoad: false
                })
                this.refs.list.style.transition = "all 0.2s ease-in-out"
                this.refs.list.style.transform = "translateY(0px)"
            }, 500)
        }
    }
    goTaskContent = (id) => {
        this.props.history.push('/grouppet/taskdetails/' + id)
        tongji('taskNote_goDetails')
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
    showDescripHandle = () => {
        this.setState({
            modal: true
        })
        tongji('task_lookDescription')
    }

    hideDescripHandle = () => {
        this.setState({
            modal: false
        })
    }
    render(){
        const {loading,listData,pageLoad,modal} =this.state
        return  (
            loading ?<LoadingAnimationA />
                :<div className="gp-container">
                    <div className="task-wrapper new-messMsgList" ref='wrapper'
                         onTouchStart={listData&&listData.length>0?this.touchStartHandle:null}
                         onTouchMove={listData&&listData.length>0?this.touchMoveHandle:null}
                         onTouchEnd={listData&&listData.length>0?this.touchEndHandle:null}>
                        <div className="title" onClick={this.showDescripHandle}>
                            <p className="title-prompt">投放说明</p>
                        </div>
                        <div className="taskList" ref='list'>
                            {
                                listData&&listData.length>0?<TaskList listData={listData} goTaskContent={this.goTaskContent}/>
                                    : <NoList type={'TASK_LIST'}/>
                            }
                        </div>
                        {
                            modal? <TaskDescrip hideHandle={this.hideDescripHandle}/>:null
                        }

                    </div>
                    <div className="pageFooterLoad">{listData&&listData&&listData.length>0&&pageLoad ? <LoadingAnimationB/> : null}</div>
                </div>
        )
    }
}