import React,{Component} from 'react'
import Input from '../shareComponents/input/Input'
import RangePicker from '../shareComponents/rangePicker/RangePicker'
import SelectBox from '../shareComponents/selectBox/SelectBox'
import PageFragRule from '../shareComponents/pageFrag/PageFragRule'
import {problem_list, export_excel,problems} from "../../funStore/CommonPort";
import Table from './Table'
import {API_URL} from "../../constants/Api";
import '../../assets/css/reviewIndex.scss'
export default class FeedbackMain extends Component{
    constructor(props){
        super(props)
        this.state={
            params: {},
            problemTitle:[],
            problemId:[],
            pageInfo:{
                current_page: 0,
                page_size: 100,
                total_page: 0,
                total_records:0
            },
        }
    }
    componentDidMount(){
        this.getQuestList(this.state.pageInfo.page_size)
        problems().then(resData=>{
            this.setState({
                problemTitle: resData.data?resData.data.map(item => item.title):[],
                problemId: resData.data?resData.data.map(item => item.id):[]
            })
        })
    }

    getQuestList=(page_size)=>{
        const {params} = this.state
        const url = '?current_page=0&page_size='+page_size
        problem_list(url, params).then(resData => {
            if (resData.code === 1200 && resData.data !== null) {
                this.pullData(resData)
            }
        })
    }
    pullData=(resData)=>{
        const {pageInfo} = this.state
        this.setState({
            listData: resData.data?resData.data.map(item => {
                return {
                    ...item,
                    checked: false
                }
            }):[],
            checkAll: false,
            pageInfo: resData.page_info?resData.page_info:{
                current_page:0,
                page_size: pageInfo.page_size,
                total_page:1,
                total_records:0
            }
        })
    }
    setParamasHandle=(name,value,sentList,index)=> {
        const {params} = this.state
        params[name] = value
        this.setState({params})
    }
    setDateParams = (dateString) => {
        const {params} = this.state
       if(dateString[0]!==''){
           params.commit_date_begin=dateString[0]+' 00:00:00'
           params.commit_date_end=dateString[1]+' 23:59:59'
       }else{
           delete params.commit_date_begin
           delete params.commit_date_end
       }
        this.setState({params})
    }

    exportHandle=()=>{
        export_excel(API_URL.problemExport,this.state.params,"问题反馈.xlsx")
    }
    //选择分页
    changeSize = (size) => {
        this.getQuestList(size)
    }
    render(){
        const {params,pageInfo,listData} =this.state
        return <div className='review-container'>
            <div className="searchBar">
                <Input label={'手机号码：'}  maxLength={11} name={'phone'} placeholder={'请输入手机号'} value={params.phone} handleChange={this.setParamasHandle}/>
                <SelectBox
                    selectLabel={'问题类型：'}
                    selectOption={this.state.problemTitle}
                    paramaName={'problem_id'}
                    paramaValue={this.state.problemId}
                    setParamasHandle={this.setParamasHandle}
                    all={true}
                />
                <Input label={'机器人code：'}  name={'robot_code'} placeholder={'请输入机器人code'} value={params.robot_code} handleChange={this.setParamasHandle}/>
                <Input label={'群名：'}  name={'group_name'} placeholder={'请输入群名'} value={params.group_name} handleChange={this.setParamasHandle}/>
                <RangePicker
                    label={'提交日期:'}
                    setDateParams={this.setDateParams}
                />
                <div className="btnArea">
                    <div className="searchBtn" onClick={()=>this.getQuestList(pageInfo.page_size)}>搜索</div>
                </div>
            </div>
            <div className="tableArea">
                <div className="operateArea">
                    <div className='operate-left'>
                        <div className="changeSize">
                            <span className={pageInfo!==null&&pageInfo.page_size===100?'checked':''} onClick={()=>{this.changeSize(100)}}>100</span>  |  <span className={pageInfo&&pageInfo.page_size===500?'checked':''} onClick={()=>{this.changeSize(500)}}>500</span>
                        </div>
                        <div className="totalRecords">总计：{pageInfo&&pageInfo.total_records}条</div>
                    </div>
                    <div className="operate-right">
                        <div className="exportBtn" onClick={this.exportHandle}>结果导出</div>
                    </div>
                </div>
                <Table listData={listData} pageInfo={pageInfo}/>
                {
                    pageInfo!==null&&pageInfo.total_page>1
                        ?<PageFragRule
                            url={API_URL.problemList}
                            pageSize={pageInfo.page_size}
                            pageInfo={pageInfo}
                            searchParamas={params}
                            pullData={this.pullData}
                        />:''
                }
            </div>
        </div>
    }
}