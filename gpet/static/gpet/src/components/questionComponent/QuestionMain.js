import React, {Component} from 'react'
import QuestionItem from './QuestionItem'
import {tongji} from '../../constants/TrackEvent'

const QuestionList = [
    {
        q: 'Q：为什么我的宠物说话没反应了？',
        a: [
            '1.主要是小宠被频繁拉群时，会导致呼吸障碍而卡死。',
            '2.请主人准备好宠物的微信名称和头像截图，然后联系在线客服进行急救，以便让宠物恢复正常工作。',
            '3.也可以关注小宠微信公众号“微小宠World”进行问题反馈哦~'
        ],
        isExpand: false
    },
    {
        q: 'Q：为什么加宠物好友不通过？',
        a: [
            '1.小宠只能通过微信二维码添加；',
            '2.试试用其他微信添加宠物为好友，如果添加成功，那就是主人的微信号被微信限制加好友了呢，可以尝试第二天再添加哦；',
            '3.如果主人和主人的朋友都无法添加，这是由于宠物被多人添加，导致心肺功能坏死，请主人准备好宠物二维码和宠物微信名称，并及时联系在线客服进行心肺复苏，以便尽快救活小宠，谢谢！',
            '4.也可以关注小宠微信公众号“微小宠World”进行问题反馈哦~'
        ],
        isExpand: false

    },
    {
        q: 'Q：拉宠物进群后不提示开通？',
        a: [
            '1.邀请入群后,在群内发送任意消息即可完成激活；',
            '2.宠物当天入群的额度满了，或者宠物激活的总名额已用完，如有多余的宠物会推送，没有只能等宠物生产了;',
            '3.没有激活群，请千万不要拉其他宠物再入群，请主人准备好以下资料：',
            ' (1) 宠物的名字和头像截图；',
            ' (2) 入群时发送给宠物的邀请截图；',
            ' (3) 入群时的群内信息，包含系统提示的入群邀请和激活笑脸。',
            '然后请你对宠物说纯数字5 ，联系在线客服解决，谢谢！'
        ],
        isExpand: false
    },

    {
        q: 'Q：宠物一天能开通多少群？',
        a: [
            '每个宠物能开通的群数总额是有限制的，不是每天会更新的哦，而且宠物是多人共享哒，其他主人可能会快速把群名额用完，所以拼手速的时候到啦。'
        ],
        isExpand: false
    },
    {
        q: 'Q：如何控制群内内容投放？',
        a: [
            '请主人进入小宠首页-群列表，已同步的群会出现该群内容投放的开关。另外，点击收益是3天左右结算的哦。'
        ],
        isExpand: false
    },
    {
        q: 'Q：群收益怎么查，如何提现？',
        a: [
            '请主人进入首页后，点击“群收益”版块查询，同时可以申请提现。'
        ],
        isExpand: false
    },
    {
        q: 'Q：提现多久到账？',
        a: [
            '提现申请前，请务必先进行微信账号的实名认证，然后再进行提现申请哦。',
            '申请成功后，钱款会在1-3个工作日内打到主人的微信账户。',
            '例如在周五 、周六或周日提现，则最晚在下周三晚上24点前到账，请注意查收哦。'
        ],
        isExpand: false
    },
    {
        q: 'Q：我拉小宠进一个群，能得多少红包？',
        a: [
            '主人把小宠拉进群后，小宠将会体验主人群内的舒适度。舒适度不同，红包大小不同哦~红包最大30元。'
        ],
        isExpand: false
    },
    {
        q: 'Q：为什么我的群少了？',
        a: [
            '为了能让小宠服务更多新群，小宠会不定时退出一些不活跃的、舒适度低的群呢，这样可以为主人增加新的入群额度，主人可以回复小宠“6”随时查询额度哦～'
        ],
        isExpand: false
    }
]

export default class QuestionMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            checkIndex: -1,
            listData: QuestionList
        }
        this.checkHandle = this.checkHandle.bind(this)
        this.goFeedback = this.goFeedback.bind(this)
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

    goFeedback() {
        this.props.history.push('/grouppet/feedback')
        tongji('question_goFeedback')
    }

    render() {
        const {checkIndex, listData} = this.state
        return (
            <div className='gp-container'>
                <div className="question-wrapper">
                    <div className="title"/>
                    <div className="questionList">
                        {
                            listData.map((item, index) => {
                                return <QuestionItem
                                            key={index} item={item} index={index} checkIndex={checkIndex}
                                            checkHandle={this.checkHandle}
                                        />
                            })
                        }
                    </div>
                    <div className="buttonArea">
                        <div className="clickBtn" onClick={this.goFeedback}>没有解决？点我</div>
                    </div>
                </div>
            </div>
        )
    }
}