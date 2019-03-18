import React, {Component} from 'react'
import {tongji} from '../../../constants/TrackEvent'
import LoadingAnimationA from '../../shareComponent/LoadingAnimationA'
import './index.scss'

export default class HelpMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true
        }
    }

    componentDidMount() {
        document.title = '红包攻略'
        setTimeout(() => {
            this.setState({
                loading: false
            })
        }, 100)
    }

    render() {
        return (this.state.loading ? <LoadingAnimationA/> : <HelpMainA history={this.props.history}/>)
    }
}

const HelpMainA = ({history}) => {
    return (
        <div className='gp-container'>
            <div className="help-wrapper">
                <div className="title"/>
                <div className="content">
                    <h6>一：拉群有红包，群多=红包多</h6>
                    <p> 拉小宠入群连续拿红包30天，群内越舒适红包越大，最高<span>30元/群</span>。</p>
                    <div className='img_1'>
                        <button className='goLook'
                                onClick={() => {
                                    history.push('/grouppet/star');
                                    tongji('hongbaoHelp_click_shuShiDuBtn');
                                }}>舒适度说明书
                        </button>
                    </div>
                </div>
                <div className="content">
                    <h6>二：群内投内容，点击多=红包多</h6>
                    <p>小宠发到群内的段子、新闻或福利（下图案例）。群友每次阅读你都有<span>0.16元红包</span>，点击越多红包越多哦～</p>
                    <div className='img_2'/>
                    <div className="subtitle">Tips:</div>
                    <p style={{marginBottom: '20px'}}>如果担心小宠发的消息打扰群友，你可以在对应的群列表内选择关闭哦～</p>
                </div>
                <div className="content">
                    <h6>三: 邀请有红包，收徒多=红包多</h6>
                    <p>生成你的收徒海报，并分享给好友。好友扫码注册后就成为你的徒弟。徒弟徒孙的群奖励和点击红包你都有分佣拿！</p>
                    <p style={{marginTop: '30px'}}>
                        <span>徒弟拉群你可以分佣 100%，0.02元/点击<br/>徒孙拉群你可以分佣 50%，0.02元/点击</span>
                    </p>
                    <p className='zhushi'>注：如徒弟拉群收益30元，你也收益30元</p>
                    <div className='img_3'/>
                    <div className="btnbox" onClick={() => {
                        history.push('/grouppet/share');
                        tongji('hongbaoHelp_click_shareBtn');
                    }}>生成海报
                    </div>
                </div>
                <div className="footer">
                    <h6>-举个栗子-</h6>
                    <div className="example1 example1_B">
                        <div className="image"/>
                        <div className="text">微小宠你好，我身边的微信群很少，大概就五六个。一个月能赚多少钱？</div>
                    </div>
                    <div className="example2 example2_B">
                        <div className="image"/>
                        <div className="text">假设你拉小宠进了五个群，舒适度为三个笑脸。再推荐10名好友一起使用微小宠。然后小宠每天会在群内分享1-2篇文章，预计一个群1至2人阅读。</div>
                    </div>
                    <div className="example2 example3_B">
                        <div className="image"/>
                        <div className="text">
                            <p><span>拉群红包:</span><span>5个群*3元=15元</span></p>
                            <p><span>收徒红包:</span><span>10个徒弟*3元*5个群=150元</span></p>
                            <p><span>点击收益:</span><span>0.16元/点击*2人/群*55个群*30天≈528元/月</span></p>
                            <div>
                                总计：693元/月<br/>
                                <p className='highlight_red'>相当于25万存在余额宝一个月的收益哦!</p>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}