import React, {Component} from 'react'

const stars = [1, 2, 3, 4, 5]
export default class repullHandleGroupItem extends Component {
    constructor(props) {
        super(props)
        this.state = {
            maxHeight: 0,
            minHeight: 0,
            startTime: 0
        }
    }

    componentDidMount() {
        this.setState({
            maxHeight: this.refs.cardHeader.offsetHeight + this.refs.cardDetail.offsetHeight,
            minHeight: this.refs.cardHeader.offsetHeight
        })
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.item.id !== this.props.item.id) {
            this.setState({
                maxHeight: this.refs.cardHeader.offsetHeight + this.refs.cardDetail.offsetHeight,
                minHeight: this.refs.cardHeader.offsetHeight
            })
        }
    }

    render() {
        const {maxHeight, minHeight} = this.state
        const {item, checkHandle, showRobot, handleSwitch} = this.props
        return (
            <div className="groupItem" style={{height: item.expand ? maxHeight + 'px' : minHeight + 'px'}}>
                <div ref="cardHeader" className="cardHeader" onClick={() => {checkHandle(item)}}>
                    {
                        // old_group 判断新群和老群 0 新群 1 老群
                        item.old_group===0? <div>
                            <div className='stars'>
                                {stars.map((v, i) => {
                                    return <span key={i} className={`${item.quality_level < v ? '' : 'icon_star'}`}/>
                                })}
                            </div>
                            <span className='status'>{item.income_status}</span>
                        </div>:null
                    }
                    <div>
                        <span className='groupName'>{item.name ? item.name : '未命名'}</span>
                        <span className={item.expand ? "unexpand expand" : "unexpand"}>{item.expand ? "收起" : "展开"}</span>
                    </div>
                </div>
                <div ref="cardDetail" className="cardDetail">
                    <div className="leftBox">
                        {
                            item.old_group===0?<div className="profit">入群红包：{item.group_income}元（已收益{item.settle_count}天）</div>:null
                        }
                        <div className="tips">点击红包：{item.text_income}元/点击</div>
                        {
                            <div className='robotNameBox'>
                                <span className='nickname'>群昵称：{item.robot_name}</span>
                                <span className='chNameBtn' onClick={() => showRobot(item)}>修改</span>
                            </div>
                        }
                    </div>
                    <div className="rightBox">
                        {/*//投放开关 0 关 1 开*/}
                        {
                            <div className='launchSwitch' onClick={()=>handleSwitch(item)}>
                                {item.launch_switch === 1 ? '打开：' : '关闭：'}
                                <div className={item.launch_switch === 1 ? 'bg open' : 'bg'}>
                                    <div className="circle"/>
                                </div>
                            </div>

                        }
                    </div>
                </div>
            </div>
        )
    }
}
