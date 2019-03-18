import React, { Component } from 'react'
import { getSearch } from '../../../funStore/CommonFun'
import './index.scss'
export default class Index extends Component {
    constructor(props) {
        super(props)
        this.state = {
            current: 0
        }
        this.checkHandle = this.checkHandle.bind(this)
    }
    componentDidMount() {
        var params = getSearch()
        if (params.status === 'error') {
            this.setState({
                current: 1
            })
        }
    }
    checkHandle(index, type) {
        this.setState({
            current: index
        })
        this.props.changeNav && this.props.changeNav(type)
    }
    render() {
        const { current } = this.state
        const { nav } = this.props
        return (
            <div className='new-ym-navibar'>
                <div className="navibar">
                    <div className="navi">
                        {
                            nav.map((item, index) => {
                                return (
                                    <div className={current === index ? 'item active' : 'item'} key={index}
                                         onClick={() => { this.checkHandle(index,item.type) }}>
                                        <span className='text'>{item.text}</span>
                                        <span className='num'>{item.num}</span>
                                    </div>
                                )
                            })
                        }
                    </div>
                    <div className="bar" style={{left:current===0?'13%':'63%'}}/>
                </div>
            </div>

        )
    }
}