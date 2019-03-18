import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import DataList from './DataList'
import {formatDate} from '../../funStore/CommonFun'
import MsgEmpty from '../shareComponent/MsgEmpty'
import {OwnerIsGroup, group_statistics} from '../../funStore/CommonPort'
import './index.scss'

const beforeDay = () => {
    let before = new Date().getTime() - 24 * 60 * 60 * 1000;
    let arr = formatDate(before, 'yy/mm/dd').split('/')
    return arr[1] + '月' + arr[2] + '日'
}
export default class GroupDataMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasGroup: true,//是否有导群
            pageInfo: {
                current_page: 0,
                page_size: 20,
                total_page: 0,
            },
            data: [],
            request: true
        }
    }

    componentDidMount() {
        document.title = '群管理';
        //1.判断用户是否有群主群
        let self = this
        OwnerIsGroup().then(res => {
            if (res.code === 1200 && res.data) {
                //2.获取群数据列表
                self.requestList(this.state.pageInfo.current_page, this.state.pageInfo.page_size)
            } else {
                self.setState({
                    isHasGroup: false,
                    loading: false
                })
            }
        })
    }

    requestList = (current_page, page_size) => {
        if (!this.state.request) return
        this.setState({request: false})
        group_statistics(`current_page=${current_page}&page_size=${page_size}`).then(resData => {
            this.setState({
                request: true,
                data: this.state.data.concat(resData.data),
                pageInfo: resData.page_info,
                loading: false
            })
        }).catch(err => {
            this.setState({
                loading: false,
                request: true,
            })
        })
    }

    requestData = () => {
        const {pageInfo} = this.state
        if (pageInfo.total_page > pageInfo.current_page + 1) {
            this.requestList(pageInfo.current_page + 1, pageInfo.page_size)
        }
    }

    render() {
        const {loading, data, isHasGroup} = this.state
        return (
            loading ? <LoadingAnimationA/>
                : isHasGroup ? <div className="gp-container">
                    <div className="data-wrapper">
                        <div className="title">
                            <p style={{marginRight: '220px'}}>*所有群数据均为{beforeDay()}数据</p>
                        </div>
                        <DataList data={data} requestData={this.requestData}/>
                    </div>
                </div> : <MsgEmpty type={2}/>
        )
    }
}