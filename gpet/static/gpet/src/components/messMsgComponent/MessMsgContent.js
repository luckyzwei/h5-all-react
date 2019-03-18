import React, {Component} from 'react'
import {Text, Link, Wxapp, Pic} from "../shareComponent/msgType/MsgTypeUnit";
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {format_date} from '../../funStore/CommonFun'
import {get_massmsg_content} from '../../funStore/CommonPort'

export default class MessMsgContent extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            data: []
        }
    }

    componentDidMount() {
        document.title = '群发消息'
        let self = this
        let id = this.props.match.params.id
        get_massmsg_content(`${id}/message`).then(resData => {
            if (resData.code === 1200 && resData.data) {
                self.setState({
                    data: resData.data,
                })
            }
            self.setState({
                loading: false
            })
        })
    }

    render() {
        const {loading, data} = this.state
        return (
            loading ? <LoadingAnimationA/>
                : <div className='new-messMsgList'>
                    <div className="header">
                        <div className="title"/>
                    </div>
                    <div className='new-messMsgContent'>
                        <div className="messContent">
                            <div className="title">
                                群发信息 {data !== null && data.send_date ? format_date(data.send_date, 'MM/DD HH:MM') : ''}
                            </div>
                            <div className='content'>
                                <div className="content-title">群发内容</div>
                                <div className="msgtype-content-info">
                                    <div className="taskTitle">
                                        <img src={"/images/banner/title6.png"} alt="" />
                                    </div>
                                    <div className="previewBox">
                                        {
                                            data !== null && data.content !== null ? data.content.map((item, i) => {
                                                //3:文字，8:图片，9:语音，6:链接，11:小程序
                                                return (
                                                    item.type === 3 && item.content !== ''
                                                        ? <Text item={item} key={i}/>
                                                        : item.type === 6
                                                        ? <Link item={item} key={i}/>
                                                        : item.type === 11
                                                            ? <Wxapp item={item} key={i}/>
                                                            : item.type === 8
                                                                ? <Pic item={item} key={i}/> : ''
                                                )
                                            }) : ''
                                        }
                                    </div>
                                </div>
                            </div>

                        </div>
                        <div className="messRange">
                            <div className="title">
                                <span>群发范围</span>
                            </div>
                            <ul>
                                {
                                    data.groups_info !== null ? data.groups_info.map((item, index) => {
                                        return <li key={index}>
                                            <span>{item.name}</span>
                                        </li>
                                    }) : ''
                                }
                            </ul>

                        </div>
                    </div>

                </div>
        )

    }
}
