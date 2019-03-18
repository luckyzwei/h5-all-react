import React, {Component} from 'react'
import RangePicker from '../shareComponents/rangePicker/RangePicker'
import SelectBox from '../shareComponents/selectBox/SelectBox'
import Input from '../shareComponents/input/Input'
import Table from './Table'
import PageFragRule from '../shareComponents/pageFrag/PageFragRule'
import Modal from './modal/Modal'
import {sendEvent} from '../../funStore/CommonFun'
import {review_list, review} from '../../funStore/CommonPort'
import {API_URL} from "../../constants/Api";
import '../../assets/css/reviewIndex.scss'
export default class ReviewMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            params: {
                sort: {
                    // # sort_key: amount/create_date/paid_date, value:asc(正序)/desc(倒序)
                    sort_key: 'create_date',
                    value: 'desc'
                },
            },
            listData: [],
            pageInfo: {
                "current_page": 0,
                "page_size": 100,
                "total_page": 0
            },
            checkAll: false,
            showModal: null,
            checkId: '',
            total: 0.00
        }
    }

    componentDidMount() {
        this.refresh()
    }

    refresh=()=>{
        const {pageInfo} =this.state
        this.getReviewList(pageInfo.current_page,pageInfo.page_size)
    }

    getReviewList = (current_page,page_size) => {
        const {params} = this.state
        const url = '?current_page='+current_page+'&page_size='+page_size
        review_list(url, params).then(resData => {
            if (resData.code === 1200 && resData.data !== null) {
                this.pullData(resData)
            }
        })
    }

    pullData = (resData) => {
        this.setState({
            listData: resData.data ? resData.data.map(item => {
                return {
                    ...item,
                    checked: false
                }
            }) : [],
            checkAll: false,
            pageInfo: resData.page_info
        })
    }
    setParamasHandle = (name, value, sentList, index) => {
        let params = this.state.params
        params[name] = value
        this.setState({
            params: params
        })
    }
    setDateParams = (dateString, name) => {
        let {params} = this.state
        switch (name){
            case 'startTime'://提现日期
                if(dateString[0]!==''&&dateString[1]!==''){
                    params.withdraw_date_begin = dateString[0] + ' 00:00:00'
                    params.withdraw_date_end = dateString[1] + ' 23:59:59'
                }else{
                    delete params.withdraw_date_begin
                    delete params.withdraw_date_end
                };
                break;
            case 'endTime':
                if(dateString[0]!==''&&dateString[1]!==''){
                    params.paid_date_begin = dateString[0] + ' 00:00:00'
                    params.paid_date_end = dateString[1] + ' 23:59:59'
                }else{
                    delete params.paid_date_begin
                    delete params.paid_date_end
                };
                break;
            default:
                break;
        }
        this.setState({params})
    }

    showModalHandle = (text, id) => {
        if (this.state.listData.find(item => item.status === 0 && item.checked) || id) {
            this.setState({
                showModal: text
            })
            if (id) {
                this.setState({
                    checkId: id
                })
            }
        }
    }
    hideModalHandle = () => {
        this.setState({
            showModal: null
        })
    }
    //选择分页
    changeSize = (size) => {
        this.getReviewList(0,size)
    }

    //金额／提现日期／打款日期排序查询
    sortHandle = (sortName) => {
        let {params, pageInfo} = this.state
        let newSort ={
            sort_key:sortName,
            value: params.sort.sort_key===sortName?params.sort.value==='desc'?'asc':'desc':'desc'
        }
        params.sort= newSort
        this.setState({params}, () => {
            this.getReviewList(0,pageInfo.page_size)
        })

    }

    reviewHandle = (id, status) => {
        // 单个审核 1:通过，2:拒绝
        const params = {
            withdraw_id: [id],
            status: status
        }
        // console.log(params, '单个 params===')
        review(params).then(res=>{
            this.hideModalHandle()
            if(res.code===1200){
                this.refresh()
                if(params.status===1){
                    sendEvent("messages",{msg:"审核通过成功",status:200,timer:2000})
                }else{
                    sendEvent("messages",{msg:"拒绝通过成功",status:200,timer:2000})
                }
            }else{
                if(params.status===1){
                    sendEvent("messages",{msg:"审核通过失败",status:201,timer:2000})
                }else{
                    sendEvent("messages",{msg:"拒绝通过失败",status:201,timer:2000})
                }
            }
        })
    }
    batchReviewHandle = (status) => {
        // 批量审核
        const {listData} = this.state
        const params = {//待审核的 选中的
            withdraw_id: listData.filter(item => item.status === 0 && item.checked).map(item => item.id),
            status: status
        }
        // console.log(params, '多个 params===')
        review(params).then(res=>{
            this.hideModalHandle()
            if(res.code===1200){
                this.refresh()
                if(params.status===1){
                    sendEvent("messages",{msg:"审核通过成功",status:200,timer:2000})
                }else{
                    sendEvent("messages",{msg:"拒绝通过成功",status:200,timer:2000})
                }
            }else{
                if(params.status===1){
                    sendEvent("messages",{msg:"审核通过失败",status:201,timer:2000})
                }else{
                    sendEvent("messages",{msg:"拒绝通过失败",status:201,timer:2000})
                }
            }
        })
    }

    checkAllHandle = () => {
        let {checkAll, listData} = this.state
        this.setState({
            checkAll: !checkAll,
            listData: listData.map(item => {
                return {
                    ...item,
                    checked: !checkAll
                }
            })
        }, this.calculateTotal)
    }
    checkHandle = (id) => {
        let {listData} = this.state
        let listUncheck = listData.filter(item => item.status === 0 && !item.checked)
        this.setState({
            checkAll: listUncheck.length === 1 && listUncheck[0].id === id,
            listData: listData.map(item => {
                return item.id === id ? {
                    ...item,
                    checked: !item.checked
                } : item
            })
        }, this.calculateTotal)
    }
    calculateTotal = () => {
        var total = 0
        this.state.listData.forEach(item => {
            if (item.status === 0 && item.checked) {
                total += parseFloat(item.amount)
            }
        });
        this.setState({
            total: total.toFixed(2)
        })


    }

    render() {
        const {params, pageInfo, listData} = this.state
        return <div className='review-container'>
            <div className="searchBar">
                <Input label={'手机号码：'} maxLength={11} name={'phone'} placeholder={'请输入手机号'} value={params.phone}
                       handleChange={this.setParamasHandle}/>
                <div className="amountRange">
                    <Input label={'金额范围：'} maxLength={9} placeholder={'起始金额'}
                           name={'amount_begin'}
                           value={params.amount_begin} handleChange={this.setParamasHandle}/>
                    <div className="line"/>
                    <Input name={'amount_end'} value={params.amount_end}
                           maxLength={9} placeholder={'结束金额'}
                           handleChange={this.setParamasHandle}/>
                </div>
                <RangePicker
                    label={'提现日期:'}
                    paramaName={'startTime'}
                    setDateParams={this.setDateParams}
                />
                <RangePicker
                    label={'打款日期:'}
                    paramaName={'endTime'}
                    setDateParams={this.setDateParams}
                />
                <SelectBox
                    selectLabel={'打款状态：'}
                    selectOption={['待审核', '打款中', '未通过', '已打款', '打款失败']}
                    paramaName={'status'}
                    paramaValue={[0, 1, 2, 3, 4]}
                    setParamasHandle={this.setParamasHandle}
                    all={true}
                />
                <div className="btnArea">
                    <div className="searchBtn" onClick={() => this.getReviewList(0,pageInfo.page_size)}>搜索</div>
                </div>
            </div>
            <div className="tableArea">
                <div className="operateArea">
                    <div className='operate-left'>
                        <div className="changeSize">
                            <span className={pageInfo !== null && pageInfo.page_size === 100 ? 'checked' : ''} onClick={() => {this.changeSize(100)}}>100</span> | <span className={pageInfo && pageInfo.page_size === 500 ? 'checked' : ''} onClick={() => {this.changeSize(500)}}>500</span>
                        </div>
                        <div className="totalRecords">总计：{pageInfo && pageInfo.total_records}条</div>
                    </div>
                    <div className="operate-right">
                        <div className="rejectBtn" onClick={() => {this.showModalHandle('batchReject')}}>批量拒绝通过</div>
                        <div className="acceptBtn" onClick={() => {this.showModalHandle('batchAccept')}}>批量审核通过</div>
                    </div>
                </div>
                <Table listData={listData}
                       params={params}
                       pageInfo={pageInfo}
                       checkAll={this.state.checkAll}
                       showModalHandle={this.showModalHandle}
                       checkAllHandle={this.checkAllHandle}
                       checkHandle={this.checkHandle}
                       sortHandle={this.sortHandle}
                />

                {
                    pageInfo !== null && pageInfo.total_page > 1
                        ? <PageFragRule
                            url={API_URL.reviewList}
                            pageSize={pageInfo.page_size}
                            pageInfo={pageInfo}
                            searchParamas={params}
                            pullData={this.pullData}
                        /> : ''
                }
            </div>
            {
                this.state.showModal !== null
                    ? <Modal
                        status={this.state.showModal}
                        hideModalHandle={this.hideModalHandle}
                        reviewHandle={this.reviewHandle}
                        batchReviewHandle={this.batchReviewHandle}
                        checkId={this.state.checkId}
                        total={this.state.total}
                    /> : ''
            }
        </div>
    }
}