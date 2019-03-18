import React, {Component} from 'react';
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import './index.css'

export default class HomeMain extends Component {
    componentDidMount() {
        document.title='个人中心'
    }

    onTouchSetting=(item)=> {
        this.props.history.push('/demo/throwin?name=' + encodeURIComponent(item.name) + '&code=' + item.code+'&id='+item.id)
    }

    render() {
        const {groupList} = this.props
        return (

            groupList
                ?
                <div className="App home">
                    <div className="header-view">
                        <div className="top-box">
                            <div className="title">可提现金额(元）</div>
                            <div className="account">0.00</div>
                        </div>
                        <div className="get-out">提现</div>
                        <div className="bottom-box">
                            <div className="left-box">
                                <div className="title">累计金额(元)</div>
                                <div className="account">0.00</div>
                            </div>
                            <div className="line"/>
                            <div className="right-box">
                                <div className="title">待结算(元)</div>
                                <div className="account">0.00</div>
                            </div>
                        </div>
                    </div>
                    <div className="group-info">
                        <div className="intro">群列表</div>
                        <div className="group-box">
                            {
                                groupList.map((item, index) => {
                                    return (
                                        <div key={index}>
                                            {
                                                index === 0 ? null : <div className="line"></div>
                                            }
                                            <div className="item" key={index}>
                                                <div className="title">{item.name}</div>
                                                <div className="setting" onTouchEnd={() => {
                                                    this.onTouchSetting(item)
                                                }}>
                                                    <div>设置</div>
                                                </div>

                                            </div>

                                        </div>

                                    )
                                })
                            }
                        </div>
                    </div>

                </div> : <LoadingAnimationA/>


        )
    }
}


