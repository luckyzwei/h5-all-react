import React, {Component} from 'react'
import NaviBar from '../shareComponent/Navibar/Index'
import LoadingAnimationB from '../shareComponent/LoadingAnimationB'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {tongji} from '../../constants/TrackEvent'
import DiscipleItem from './DiscipleItem'
import Modal from './Modal'
import {disciple_list} from '../../funStore/CommonPort'
import {format_date} from '../../funStore/CommonFun'
import {NoList} from '../shareComponent/notList'
import {DiscipleRule} from '../shareComponent/modalDescrip/ModalDescrip'
import {history} from '../../index'
import './index.scss'
// 加载高度
const loadingHeight = -80
export default class DiscipleList extends Component {
    constructor(props) {
        super(props)
        this.state = {
            startPos: 0,
            bottomDistance: 0,
            pageLoading: true,
            loading: false,
            listData: [],
            pageInfo: {
                current_page: null,
                page_size: 20,
                total_page: 0
            },
            type: 1,
            templateData: {
                '1': {
                    pageInfo: {
                        current_page: null,
                        page_size: 20,
                        total_page: 0
                    },
                    listData: []
                },
                '2': {
                    pageInfo: {
                        current_page: null,
                        page_size: 20,
                        total_page: 0
                    },
                    listData: []
                }
            },
            nav: [
                {text: '我的徒弟', type: 1, num: '(0)'},
                {text: '我的徒孙', type: 2, num: '(0)'}
            ],
            checkIndex: -1,
            modalFlag: '',
            modal:false
        }
        this.touchStartHandle = this.touchStartHandle.bind(this)
        this.touchMoveHandle = this.touchMoveHandle.bind(this)
        this.touchEndHandle = this.touchEndHandle.bind(this)
        this.pullList = this.pullList.bind(this)
        this.scrollLoad = this.scrollLoad.bind(this)
        this.changeNav = this.changeNav.bind(this)
        this.checkHandle = this.checkHandle.bind(this)
        this.showModal = this.showModal.bind(this)
    }

    componentDidMount() {
        // leave=1徒弟列表,leave=2徒孙列表
        const url_depth1 = `current_page=0&page_size=${this.state.pageInfo.page_size}&leave=1`
        const url_depth2 = `current_page=0&page_size=${this.state.pageInfo.page_size}&leave=2`
        let p1 = disciple_list(url_depth1)
        let p2 = disciple_list(url_depth2)
        Promise.all([p1, p2]).then(values => {
            let {templateData, nav, pageInfo, type, listData} = this.state
            values.forEach((v, i) => {
                templateData[i + 1].pageInfo = v.page_info
                templateData[i + 1].listData = v.data != null ? v.data.map(item => {
                    return {...item, isExpand: false}
                }) : []
                nav[i].num = ''
                nav[i].num = `${nav[i].num}(${v.page_info.total_records ? v.page_info.total_records : 0})`
            })
            pageInfo = templateData[type].pageInfo
            listData = templateData[type].listData
            this.setState({listData, pageInfo, templateData, nav: nav, pageLoading: false})
        })
    }

    touchStartHandle(e) {
        const {loading} = this.state
        if (loading) return
        const listEle = this.refs.wrapper
        let {scrollHeight, scrollTop, clientHeight} = listEle
        //记录触摸位置以及距离底部位置
        this.setState({
            startPos: e.touches[0].pageY,
            bottomDistance: scrollHeight - scrollTop - clientHeight
        })
    }

    touchMoveHandle(e) {
        const {startPos, bottomDistance, loading, listData} = this.state
        if (loading) return
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
        const {startPos, bottomDistance, loading} = this.state
        if (loading) return
        let distance = e.changedTouches[0].pageY - startPos
        let offset = distance + bottomDistance
        offset = offset < loadingHeight ? loadingHeight : offset
        // 到达最大高度加载，否则取消，返回原位置
        if (offset === loadingHeight) {
            if (!loading) {
                this.setState({
                    loading: true
                }, this.pullList)
            }
        }
    }

    pullList() {
        this.scrollLoad()
    }

    scrollLoad() {
        const {pageInfo, type, listData} = this.state
        if (pageInfo !== null && (pageInfo.current_page === null || (pageInfo.current_page + 1 < pageInfo.total_page))) {
            const url = `current_page=${pageInfo.current_page === null ? '0' : pageInfo.current_page + 1}&page_size=${10}&leave=${type}`
            disciple_list(url).then(res => {
                this.setState({
                    pageInfo: res.page_info,
                    listData: listData.concat(res.data.map(item => {
                        return {...item, isExpand: false}
                    })),
                    loading: false
                }, () => {
                    setTimeout(() => {
                        this.refs.list.style.transform = "translateY(0px)"
                    }, 100)
                })
            }).catch(err => {
                console.log(err)
            })
        } else {
            // 假拉列表
            setTimeout(() => {
                this.setState({
                    loading: false
                })
                this.refs.list.style.transform = "translateY(0px)"
            }, 500)
        }
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

    checkHandle(index) {
        this.setState({
            checkIndex: index,
            listData: this.state.listData.map((item, id) => {
                return id === index ? {
                    ...item,
                    isExpand: !item.isExpand
                } : {
                    ...item,
                    isExpand: false
                }
            })
        })
    }

    showModal(type) {
        this.setState({
            modalFlag: type
        })
    }

    goToShare = () => {
        history.push('/grouppet/share')
        tongji('disciple_clickGoShouTu')
    }

    showDescripHandle = () => {
        this.setState({
            modal: true
        })
        tongji('disciple_description')
    }

    hideDescripHandle = () => {
        this.setState({
            modal: false
        })
    }

    render() {
        const {listData, pageLoading, loading, nav, type, checkIndex, modalFlag,modal} = this.state
        return (
            pageLoading ? <LoadingAnimationA/>
                : <div className='disciple-wrapper'>
                    <div className="inner"
                         ref="wrapper"
                         onTouchStart={this.touchStartHandle}
                         onTouchMove={this.touchMoveHandle}
                         onTouchEnd={this.touchEndHandle}
                    >
                        <div className="header">
                            <div className="title"/>
                            <p onClick={this.showDescripHandle}>奖励规则</p>
                        </div>
                        <NaviBar nav={nav} changeNav={this.changeNav}/>
                        <ul ref="list" className='ulHeigth'>
                            {
                                listData && listData.length > 0 ? listData.map((item, index) => {
                                    return type === 1
                                        ? <DiscipleItem key={index} index={index} checkIndex={checkIndex} item={item}
                                                        checkHandle={this.checkHandle}
                                                        showModal={this.showModal}/>
                                        : <li key={index}>
                                            <div className="groupName">{item.name ? item.name : '待同步'}</div>
                                            <div className="time">{format_date(item.create_date, 'YYYY/MM/DD')}</div>
                                        </li>

                                }) : <NoList type={'DISCIPLE_LIST'}/>
                            }
                        </ul>
                    </div>
                    <div className="loadingBox">{listData && listData.length > 0 && loading ?
                        <LoadingAnimationB/> : ''}</div>
                    {modalFlag !== '' ? <Modal modalFlag={modalFlag} showModal={this.showModal}/> : ''}
                    <div className="saveBtn shareBtn" onClick={this.goToShare}>马上收徒</div>
                    {modal?<DiscipleRule hideHandle={this.hideDescripHandle}/>:null}
                </div>

        )
    }
}
