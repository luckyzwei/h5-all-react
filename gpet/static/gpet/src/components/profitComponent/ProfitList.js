import React, {Component} from 'react'
import ListItem from './ListItem'
import {tongji} from '../../constants/TrackEvent'

export default class ProfitList extends Component {
    constructor(props) {
        super(props)
        this.state = {
            listData: [],
            checkIndex: -1
        }
        this.checkHandle = this.checkHandle.bind(this)
    }

    componentDidMount() {
        this.setState({
            listData: this.props.profitList.map(item => {
                return {
                    ...item,
                    isExpand: false
                }
            })
        })
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.profitList.length > this.state.listData.length) {
            this.setState({
                listData: nextProps.profitList.map(item => {
                    return {
                        ...item,
                        isExpand: false
                    }
                })
            })
        }
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

    render() {
        const {listData, checkIndex} = this.state
        return (
            <div className="profitList">
                <div className="title" style={{border: listData.length === 0 ? '0 none' : ''}}
                     onClick={() => {
                         this.props.showDescripHandle();
                         tongji('profirt_lookDescription');
                     }}>最近15天明细(元)<span/></div>
                <ul>
                    {
                        listData.map((item, index) => {
                            return <ListItem key={index} index={index} checkIndex={checkIndex}
                                             checkHandle={this.checkHandle} isExpand={item.isExpand} item={item}/>
                        })
                    }
                </ul>
            </div>
        )
    }
}