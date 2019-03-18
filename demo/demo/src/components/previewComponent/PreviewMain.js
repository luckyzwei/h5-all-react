import React, {Component} from 'react';
import {get_ads} from '../../funStore/CommonPort'
import {getQueryString} from "../../funStore/CommonFun";
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import './index.css'

export default class PreviewMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            adsData: null,
            //data:{
            // launch:{},
            //ads:[]
        }
    }

    componentDidMount() {
        document.title='投放预览'
        let group_id = getQueryString('id')
        get_ads(group_id).then(res => {
            console.log(res)
            this.setState({
                adsData: res.data
            })
        })
    }

    handleGoH5 = (url) => {
        window.location.href = url
    }

    render() {
        const {adsData} = this.state
        return (
            adsData ? <div className="App preview">
                <div className="mess">根据你选择的投放类型及次数，可能投放的内容为：</div>
                <div className="top-box">
                    <div className="group">
                        <div className="intro">投放的群：</div>
                        <div className="info">{adsData.launch.group_name}</div>
                    </div>
                    <div className="date">
                        <div className="intro">投放时间：</div>
                        <div className="info">{adsData.launch.dates.join('/')}</div>
                    </div>
                    <div className="area">
                        <div className="intro">投放地区：</div>
                        <div className="info">{adsData.launch.region}</div>
                    </div>
                </div>
                <div className="content-list">
                    {
                        adsData.ads.map((item, index) => {
                            return (
                                <div className="item" key={index} onClick={() => this.handleGoH5(item.landing_url)}>
                                    <div className="title">{item.title}</div>
                                    <div className="bottom-box">
                                        <div className="desc">{item.description}</div>
                                        <img className="image" src={item.image_url} alt=""/>
                                    </div>
                                    <div className="tab">{item.label_name}</div>
                                </div>
                            )
                        })
                    }
                </div>
            </div> : <LoadingAnimationA/>
        );
    }
}


