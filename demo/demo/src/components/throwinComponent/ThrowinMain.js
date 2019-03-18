import React, {Component} from 'react';
import ChRobotName from './ChRobotName'
import Picker from 'antd-mobile/lib/picker'
import 'antd-mobile/lib/picker/style/css'
import {cityData} from './Area'
import {get_labels, set_ads, get_robot_name, change_robot_name} from '../../funStore/CommonPort'
import {getCookie, getQueryString, saveCookie} from "../../funStore/CommonFun";
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import ChangeDate from './ChangeDate'
import './index.css'

export default class ThrowinMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            changeStatus: false,
            changeName: false,
            robot_name: null,
            changeDateStatus: false,
            sensitCheck: true,//安全标准
            labels: null,
            parmas: {
                "label_ids": null, //int
                "date": ['9:00', '12:00', '16:00', '19:00', '21:00'],
                "group_name": decodeURIComponent(getQueryString('name')),
                "region": '山东省威海市市辖区'
            },
            timeData: [
                {'date': '9:00', 'selected': true},
                {'date': '12:00', 'selected': true},
                {'date': '16:00', 'selected': true},
                {'date': '19:00', 'selected': true},
                {'date': '21:00', 'selected': true}
            ],
            pickerValue: ["370000", "371000", "371001"]


        }

    }

    componentDidMount() {
        document.title = '投放设置'
        this.getLabels()
        this.getNickname()
    }

    getLabels = () => {
        const {parmas} = this.state
        let parmasCookie = JSON.parse(getCookie('parmas'))
        get_labels().then(res => {
            if (parmasCookie) {
                parmasCookie.group_name = decodeURIComponent(getQueryString('name'))
                parmasCookie.label_ids.forEach(item => {
                    res.data.forEach(v => {
                        if (v.lable_id === item || v.selected) {
                            v.selected = true
                        } else {
                            v.selected = false
                        }
                    })

                })
            } else {
                res.data.forEach((v) => {
                    v.selected = false
                })
            }

            this.setState({
                parmas: parmasCookie ? parmasCookie : parmas,
                labels: res.data,
                loading: false
            })
        })
    }
    getNickname = () => {
        let group_id = getQueryString('id')
        get_robot_name(group_id).then(res => {
            if (res.data) {
                this.setState({
                    robot_name: res.data
                })
            }
        })
    }

    showRobotName = () => {
        this.setState({
            changeStatus: true,
            sensitCheck: true
        })
    }
    hideRobotName = () => {
        this.setState({
            changeStatus: false,
            sensitCheck: true
        })
    }

    changeRobotName = (robot_name) => {
        const {changeName} = this.state
        if (changeName) return
        this.setState({changeName: true})
        let data = {
            "group_code": getQueryString('code'),
            "remark_name": robot_name
        }
        change_robot_name(data).then(res => {
            if (res.code === 1200) {
                this.setState({
                    robot_name: robot_name,
                    changeName: false
                })
                this.hideRobotName()
            }
        })
    }

    chnageSensitCheck = (state) => {
        this.setState({
            sensitCheck: state
        })
    }

    changePicker = (v) => {
        this.setState({pickerValue: v})
        this.handleArea(cityData, v)
    }

    handleArea = (data, value) => {
        const {parmas} = this.state
        let province = data.find(p => p.value === value[0])
        let city = province.children ? province.children.find(p => p.value === value[1]) : null
        let area = city.children ? city.children.find(p => p.value === value[2]) : null
        parmas.region = province.label + city.label + area.label
        this.setState({
            parmas
        })
    }

    showDateHandle = () => {
        this.setState({changeDateStatus: true})
    }

    confirmDateHandle = (dateList) => {
        const {parmas} = this.state
        parmas.date = dateList
        this.setState({
            changeDateStatus: false,
            parmas
        })
    }

    hideDateHandle = () => {
        this.setState({changeDateStatus: false})
    }

    clickTabHandle = (item, index) => {
        let that = this
        const {parmas} = this.state
        let list = this.state.labels
        list[index].selected = !list[index].selected
        this.setState({
            labels: list
        }, () => {
            let ids = []
            that.state.labels.forEach((item) => {
                if (item.selected) ids.push(item.lable_id)
            })
            parmas.label_ids = ids.length > 0 ? ids : null
            that.setState({
                parmas
            })
        })
    }

    handleSetAds = () => {
        const {parmas} = this.state
        set_ads(parmas).then(res => {
            saveCookie('parmas', JSON.stringify(parmas))
            if (res.data) {
                this.props.history.push('/demo/preview?id=' + res.data)
            }
        })
    }
    handleSave = () => {
        const {parmas} = this.state
        saveCookie('parmas', JSON.stringify(parmas))
        setTimeout(() => {
            this.props.history.push('/demo/home')
        })
    }

    changeDate = (timeData) => {
        this.setState({
            timeData: timeData
        })
    }


    render() {
        const {parmas, loading, labels, changeStatus, changeDateStatus} = this.state
        return (

            loading ? <LoadingAnimationA/>
                : <div className="throwinWrapper">
                    <div className='group-name'>
                        <div className="title flexBetween">
                            <div className='name'>微信群</div>
                            <div className='changeNameBtn' onClick={this.showRobotName}>
                                <span>小助手群昵称</span>
                                <img src={process.env.PUBLIC_URL + "/images/icon/ic_edit.png"} alt=""/>
                            </div>
                        </div>
                        <div className="group-name-content group-content textHide">
                            <span className='word green'>{parmas.group_name ? parmas.group_name : null}</span>
                        </div>
                    </div>
                    <div className="group-time">
                        <div className='name'>投放时间及频次</div>
                        <div className="group-content flexBetween textHide" onClick={this.showDateHandle}>
                            <span
                                className={`word ${parmas.date ? 'green' : 'gray'} '} textHide`}>{parmas.date ? parmas.date.join('/') : '选择时间'}</span>
                            <img src={process.env.PUBLIC_URL + "/images/icon/time.png"} alt=""/>
                        </div>
                    </div>
                    <div className="group-address">
                        <div className='name'>内容来源地区</div>
                        <Picker
                            extra="选择城市地区"
                            data={cityData}
                            value={this.state.pickerValue}
                            onChange={v => this.changePicker(v)}
                            onOk={v => this.changePicker(v)}
                        >
                            <div className="group-content flexBetween textHide">
                                <span className={`word ${parmas.region?'green':'gray'} textHide`}> {parmas.region?parmas.region:'选择城市地区'}</span>
                                <span className="downArrow"/>
                            </div>
                        </Picker>
                    </div>
                    <div className="group-type">
                        <div className='name'>
                            内容类型 <span>（请点选）</span>
                        </div>
                        <div className="group-type-content">
                            {
                                labels.map((item, index) => {
                                    return <span className='gt-item' key={index} onClick={() => {
                                        this.clickTabHandle(item, index)
                                    }}>{item.name}
                                        {
                                            item.selected ? <img src={process.env.PUBLIC_URL + "/images/icon/selected.png"}
                                                                 alt=""/> : null
                                        }
                                </span>
                                })
                            }
                        </div>
                    </div>
                    <div>
                        {
                            parmas.region && parmas.date && parmas.group_name && parmas.label_ids ?
                                <div className="throwinBtnBox flexBetween">
                                    <span className="previewBtn green" onClick={this.handleSetAds}>预览</span>
                                    <span className="saveBtn green" onClick={this.handleSave}>保存</span>
                                </div>
                                :
                                <div className="throwinBtnBox flexBetween">
                                    <span className="previewBtn gray">预览</span>
                                    <span className="saveBtn gray">保存</span>
                                </div>
                        }
                    </div>


                    {
                        changeStatus ? <ChRobotName
                            robot_name={this.state.robot_name}
                            sensitCheck={this.state.sensitCheck}
                            changeName={this.state.changeName}
                            sensitTrue={() => this.chnageSensitCheck(true)}
                            hideHandle={this.hideRobotName}
                            confirmHandle={this.changeRobotName}/> : null
                    }
                    {
                        changeDateStatus ?
                            <ChangeDate timeData={this.state.timeData}
                                        changeDate={this.changeDate}
                                        confirmHandle={this.confirmDateHandle} hideHandle={this.hideDateHandle}/> : null
                    }

                </div>
        );
    }
}


