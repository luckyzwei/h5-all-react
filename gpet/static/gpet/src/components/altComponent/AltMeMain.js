import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import MsgEmpty from '../shareComponent/MsgEmpty'
import {ErrorNoNews} from '../shareComponent/ErrorMessage'
import SwitchAlt from './SwitchAlt'
import AltMsgItem from './AltMsgItem'
import ImgPreview from './ImgPreview'
import {tongji} from "../../constants/TrackEvent";
import {OwnerIsGroup, get_altmsg, get_altswitch, chenge_altswitch} from "../../funStore/CommonPort";

export default class AltMeMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasGroup: true,//false 无
            isHasAnt: true,
            openShow: false,
            pageInfo: {
                "current_page": 0,
                "total_page": 0,
                "page_size": 20
            },
            switchStatus: null, //默认true
            messages: [],
            selectMessage: [],
            selectId: '',
            selectImg: '',
            request: true

        }
    }

    componentDidMount() {
        document.title = '有人@我'
        //1.判断用户是否有群主群
        let self = this
        OwnerIsGroup().then(res => {
            if (res.code === 1200 && res.data) {
                //2.获取群列表
                self.requestList(this.state.pageInfo.current_page, this.state.pageInfo.page_size)
                //3.是否有开启@功能
                self.getSwitch()
            } else {
                self.setState({
                    isHasGroup: false,
                    loading: false
                })
            }
        })
    }

    //获取@我信息列表
    requestList = (currentPage, pageSize) => {
        const {messages} = this.state
        if (!this.state.request) return
        this.setState({request: false})
        get_altmsg(`current_page=${currentPage}&page_size=${pageSize}`).then(resData => {
            this.setState({
                loading: false,
                request: true
            })
            if (resData.code === 1200) {
                this.setState({
                    messages: messages.concat(resData.data.map(v => ({
                        ...v,
                        isExpand: false
                    }))),
                    pageInfo: resData.page_info,

                })
            }
        })
    }

    //查看@信息 展开／收起
    expandHandle = (item) => {
        let {messages} = this.state
        messages = messages.map(v => {
            return v.msg_id === item.msg_id ? {
                ...v,
                isExpand: !v.isExpand
            } : {
                ...v,
                isExpand: false
            }
        })

        this.setState({
            messages: messages,
            selectId: item.msg_id,
            selectMessage: messages.find(v => v.msg_id === item.msg_id)
        })
    }

    //是否有开启@功能 默认开启的
    getSwitch() {
        get_altswitch().then(resData => {
            if (resData.code === 1200) {
                this.setState({
                    switchStatus: resData.data === 0 ? false : true  // 0关闭，1开启
                })
            }
        })
    }

    //是否开启@自动提醒
    showHandle = () => {
        this.setState({
            openShow: true
        })
    }

    hideHandle = (e) => {
        e.stopPropagation()
        this.setState({
            openShow: false
        })
    }

    handleSwitchStatus = () => {
        this.setState({
            switchStatus: !this.state.switchStatus
        })
    }

    handleChangeAntme = () => {
        // 知道啦
        let parmas = {alt_switch: this.state.switchStatus ? 1 : 0}
        chenge_altswitch(parmas).then(resData => {
            if (resData.code === 1200) {
                tongji('@wo_'+resData.data === 0?'close @wo':'open @wo')
                this.setState({
                    switchStatus: resData.data === 0 ? false : true  // 0关闭，1开启
                })
            }
            this.setState({
                openShow: false
            })
        })
    }


    showPreviewImg = (url) => {
        this.setState({selectImg: url})
    }
    hidePreviewImg = () => {
        this.setState({selectImg: ''})
    }
    scrollHandle = () => {
        let ele = this.refs.wrapper
        const {scrollTop, scrollHeight, offsetHeight} = ele
        if (scrollHeight - scrollTop - offsetHeight < 500) {
            this.scrollRequestList()
        }
    }
    scrollRequestList = () => {
        const {pageInfo} = this.state
        if (pageInfo.total_page > pageInfo.current_page + 1) {
            this.requestList(pageInfo.current_page + 1, pageInfo.page_size)
        }
    }

    render() {
        const {loading, isHasGroup, openShow, switchStatus, messages, selectMessage, selectId, selectImg} = this.state
        return (
            loading ? <LoadingAnimationA/> :
                (
                    isHasGroup ?
                        <div className='altme-containter'>
                            {
                                messages && messages.length > 0
                                    ?
                                    <div style={{height: '100%'}} ref="wrapper" onTouchEnd={this.scrollHandle}>
                                        <div className='altme-wrapper'>
                                            <div className="header">
                                                <div className="title"/>
                                                <div className='title-prompt' onClick={this.showHandle}>了解详情</div>
                                            </div>
                                            <div className='altmeList' ref="list">
                                                {
                                                    messages.map((item, index) => {
                                                        return <AltMsgItem key={index} message={item}
                                                                           selectMessage={selectMessage}
                                                                           selectId={selectId}
                                                                           expandHandle={this.expandHandle}
                                                                           showPreviewImg={this.showPreviewImg}/>
                                                    })
                                                }
                                            </div>
                                        </div>
                                        {selectImg ?
                                            <ImgPreview src={selectImg} hidePreviewImg={this.hidePreviewImg}/> : null}
                                    </div>
                                    : <ErrorNoNews type={1}/>

                            }
                            {openShow ? <SwitchAlt switchStatus={switchStatus}
                                                   handleChangeAntme={this.handleChangeAntme}
                                                   changeSwitch={this.handleSwitchStatus}
                                                   hideHandle={this.hideHandle}/> : null}
                        </div>
                        : <MsgEmpty type={1}/>
                )

        )
    }
}
