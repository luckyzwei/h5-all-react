import React, {Component} from 'react'
import ProfitList from './ProfitList'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import LoadingAnimationB from '../shareComponent/LoadingAnimationB'
import {PorofitDescrip} from '../shareComponent/modalDescrip/ModalDescrip'
import ProfitNewBox from './ProfitNewBox'
import {get_profit,get_profit_list} from '../../funStore/CommonPort'
import './index.scss'
export default class ProfitMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            startPos: 0,
            bottomDistance: 0,
            loading: false,
            pageInfo: null,
            profitList: [],
            pageLoad: true,
            modal: false,
            profit: null,//收益
        }
    }

    componentDidMount() {
        document.title = '收益明细'
        this.getProfit()
        this.getProfitList()
    }

    // 获取收益详情
    getProfit = () => {
        get_profit().then(resData=>{
            if (resData.code === 1200) {
                this.setState({
                    profit: resData.data.summary,
                })
            }
        })
    }

    // 获取收益明细
    getProfitList = () => {
        get_profit_list().then(resData=>{
            if (resData.code === 1200) {
                this.setState({
                    profitList: resData.data,
                    pageLoad: false
                })
            }
        }).catch(req=>{
            this.setState({
                pageLoad: false
            })
        })
    }

    showDescripHandle = () => {
        this.setState({
            modal: true
        })
    }

    hideDescripHandle = () => {
        this.setState({
            modal: false
        })
    }

    render() {
        const {loading, profitList, pageLoad, modal, profit} = this.state
        return (
            pageLoad ?
                <LoadingAnimationA/>
                : <div className='gp-container'>
                    <div className="profit-wrapper" ref="wrapper">
                        <div>
                            <ProfitNewBox history={this.props.history} profit={profit}/>
                            <ProfitList profitList={profitList} showDescripHandle={this.showDescripHandle}/>
                        </div>
                        {modal ? <PorofitDescrip hideHandle={this.hideDescripHandle}/> : null}
                    </div>
                    <div className="loadingBox">{loading ? <LoadingAnimationB/> : ''}</div>
                </div>
        )
    }
}