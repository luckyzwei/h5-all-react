import React, {Component} from 'react'
import { tongji} from '../../../constants/TrackEvent'
import {StarDescript} from './StarDescript'
import LoadingAnimationA from '../../shareComponent/LoadingAnimationA'
import './index.scss'

const list = [1, 2, 3, 4, 5]
const starBody = [{5: '30'}, {4: '9'}, {3: '3'}, {2: '1.5'}, {1: '0.6'}]
const QuestionList = [
    {
        q: '舒适度是如何得出的?',
        a: '舒适度将由人工智能的算法完成。小宠在你的帮助下会越来越聪明哦。'
    },
    {
        q: '拉群后多久出舒适度结果?',
        a: '主人拉小宠入群后，小宠将在24小时后向你推送舒适度结果（最晚不超过72小时）。',
    },
    {
        q: '舒适度是否会变化？红包是否也会变化?',
        a: '我们会定期对舒适度重新评估，如舒适度提升,红包也会立即增加。（注：舒适度提升前已发放的红包保持不变）',
    },
    {
        q: '红包如何发放?',
        a: '红包将于30天内分批发放。',
    },
    {
        q: '小宠被踢后重新拉入群，会继续获得红包吗?',
        a: '新拉小宠入群后，舒适度也会重新评估。红包天数为30天减去已发放天数。',
    }
]

export default class StarMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            starType: null,
            loading: true
        }
    }

    componentDidMount() {
        document.title = '舒适度说明'
        setTimeout(() => {
            this.setState({
                loading: false
            })
        }, 100)

    }

    showModal = (type) => {
        this.setState({
            starType: type
        })
        if(type) tongji('shuShiDu_lookCase')
    }

    render() {
        const {starType, loading} = this.state
        return (
            loading ? <LoadingAnimationA/> :
                <div className='star-wtapper'>
                    <div className="title"/>
                    <div className="content">
                        <div className='content-tips'>把「微小宠」拉入微信群后，「微小宠」将会体验群内舒适度。</div>
                        <div className='content-tips-other'/>
                        <table>
                            <thead>
                            <tr>
                                <th>舒适度</th>
                                <th>红包</th>
                            </tr>
                            </thead>
                            <tbody>
                            {
                                starBody.map((v, i) => {
                                    return <tr key={i}>
                                        <td>
                                            <div className='star'>
                                                {list.map((item, index) => {
                                                    return 6 - (i + 1) >= item ?
                                                        <span key={index} className='icon_star'/> : null
                                                })
                                                }
                                            </div>
                                            <div className='des' onClick={() => this.showModal(6 - (i + 1))}>示例</div>
                                        </td>
                                        <td>{v[6 - (i + 1)]}元</td>
                                    </tr>
                                })
                            }
                            </tbody>
                        </table>
                    </div>
                    <Question/>
                    <div className="footer">
                        <button className='GoLinkBtn'
                                onClick={() => {
                                    this.props.history.push('/grouppet/import');
                                    tongji('shuShiDu_laQunLingHongBao');
                                }}
                        >拉群领红包
                        </button>
                    </div>
                    {starType != null ? <StarDescript type={starType} hide={() => this.showModal(null)}/> : null}
                </div>
        )
    }
}
const Question = () => {
    return <div className='questions'>
        <div className="question-title">
            <span className='line'/>
            <span className='text'>常见问答</span>
        </div>
        <div className='question-content'>
            {
                QuestionList.map((item, index) => {
                    return <div className='question-item' key={index}>
                        <div className="item question">
                            <span className='num'>Q：</span>
                            <span className="text">{item.q}</span>
                        </div>
                        <div className="item answer">
                            <span className='num'>A：</span>
                            <span className="text">{item.a}</span>
                        </div>
                    </div>
                })
            }

        </div>
    </div>
}