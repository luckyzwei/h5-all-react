import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import BannerB from './roleB/BannerB'
import PeopleCard from './PeopleCard'
import {CardTitle} from './CardTitle'
import InfoBox from './InfoBox'
import {ExclusiveCard, SkillCard} from './CardBannar'
import {tongji} from '../../constants/TrackEvent'//埋点监测
import FirstLogin from '../registerComponent/FirstLogin'
import {set_marquee} from '../../funStore/CommonPort'

export default class HomepageMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            content: '',
            marquee: false  //首页是否显示跑马灯
        }
    }

    componentDidMount() {
        document.title = '首页'
        set_marquee().then(res => {
            if (res.code === 1200) {
                this.setState({
                    content: res.data.content,
                    marquee: res.data.status === 1 ? true : false
                })
            }
        })
    }

    goHelp() {
        this.props.history.push('/grouppet/help')
        tongji('home_hongBaoHelp')
    }

    goQuestion() {
        this.props.history.push('/grouppet/question')
        tongji('home_questions')
    }

    render() {
        const {guide, hideFirstGide, history, pageLoad, outlineInfo} = this.props
        const {marquee, content} = this.state
        return (
            pageLoad
                ? <LoadingAnimationA/>
                : <div className='gp-container'>
                    <div className="homepage-wrapper" style={{paddingTop: marquee ? '70px' : "0"}}>
                        {marquee ? <InfoBox content={content}/> : null}
                        <BannerB history={history}/>
                        <PeopleCard history={history} outlineInfo={outlineInfo}/>
                        <div className="featuresBox">
                            <CardTitle title={'小宠技能'}/>
                            <SkillCard history={history}/>
                        </div>
                        <div className="featuresBox">
                            <CardTitle title={'群主专享'}/>
                            <ExclusiveCard history={history}/>
                        </div>
                        <div className="footer">
                            <div className="strategy" onClick={this.goQuestion.bind(this)}>常见问题</div>
                            <div className="strategy" onClick={this.goHelp.bind(this)}>红包攻略</div>
                        </div>
                        {/*新手引导*/}
                        {guide || (!guide && localStorage.getItem('firstFlag') !== null)
                            ? <FirstLogin hideFirstGide={hideFirstGide} marquee={marquee}/> : null}
                    </div>
                </div>
        )
    }
}
