import React ,{Component} from 'react'
const statusMap = {
    '0': '待审核',
    '1': '打款中',
    '2': '未通过',
    '3': '已打款',
    '4': '打款失败'
}
export default class ReviewTable extends Component{
    constructor(props){
        super(props)
        this.state={
            checkAll:false,
            previewShow:false,
            previewCss: {
                left: 0,
                top: 0
            },
            previewId:''

        }
    }

    componentDidMount() {
        window.addEventListener('click', this.hidePreview)

    }
    componentWillUnmount() {
        window.removeEventListener('click', this.hidePreview)
    }
    hidePreview = () => {
        this.setState({
            previewShow: false
        })
    }

    previewHandle = (e,id) => {
        e.stopPropagation()
        let x = e.clientX
        let y = e.clientY
        let isTop = e.clientY < document.body.clientHeight / 2
        this.setState({
            previewShow: true,
            previewId:id
        }, () => {

            let {previewCss} = this.state
            if (isTop) {
                previewCss.left = x - 50 + 'px'
                previewCss.top = y + 'px'
            } else {
                previewCss.left = x - 50 + 'px'
                previewCss.top = y - this.refs.preview.offsetHeight + 'px'
            }
            this.setState({previewCss})
        })
    }
    render(){
        const {listData,checkAll,params,sortHandle,pageInfo,showModalHandle,checkAllHandle,checkHandle} =this.props
        return  <div className="contentTable">
            <table>
                <thead>
                <tr>
                    <td>
                        <div className="number">
                            <span className={checkAll?'icon-background checkBox checked':'icon-background checkBox'}
                                  onClick={checkAllHandle}/>
                            <span>序号</span>
                        </div>
                    </td>
                    <td>手机号</td>
                    <td>
                        金额
                        <div className="arrowBox" onClick={()=>{sortHandle('amount')}}>
                            <span className={params.sort.sort_key==='amount'&&params.sort.value==='asc'?"icon-arrow up hover":"icon-arrow up"}/>
                            <span className={params.sort.sort_key==='amount'&&params.sort.value==='desc'?"icon-arrow down hover":"icon-arrow down"}/>
                        </div>
                    </td>
                    <td>
                        提现日期
                        <div className="arrowBox" onClick={()=>{sortHandle('create_date')}}>
                            <span className={params.sort.sort_key==='create_date'&&params.sort.value==='asc'?"icon-arrow up hover":"icon-arrow up"}/>
                            <span className={params.sort.sort_key==='create_date'&&params.sort.value==='desc'?"icon-arrow down hover":"icon-arrow down"}/>
                        </div>
                    </td>
                    <td>
                        打款日期
                        <div className="arrowBox" onClick={()=>{sortHandle('paid_date')}}>
                            <span className={params.sort.sort_key==='paid_date'&&params.sort.value==='asc'?"icon-arrow up hover":"icon-arrow up"}/>
                            <span className={params.sort.sort_key==='paid_date'&&params.sort.value==='desc'?"icon-arrow down hover":"icon-arrow down"}/>
                        </div>
                    </td>
                    <td>状态</td>
                    <td>操作</td>
                </tr>
                </thead>
                <tbody>
                {
                    listData&&pageInfo?listData.map((listItem,index) => {
                        return (
                            <tr key={index}>
                                <td>
                                    <div className="number">
                                        {
                                            listItem.status===0
                                                ?<span className={listItem.checked?'icon-background checkBox checked':'icon-background checkBox'}
                                                       onClick={()=>{checkHandle(listItem.id)}}/>
                                                :null
                                        }
                                        <span>{index+1+pageInfo.current_page*pageInfo.page_size}</span>
                                    </div>
                                </td>
                                <td>{listItem.phone?listItem.phone:'-'}</td>
                                <td>{listItem.amount?listItem.amount:'-'}</td>
                                <td>{listItem.create_date?listItem.create_date:'-'}</td>
                                <td>{listItem.paid_date&&listItem.status!==2?listItem.paid_date:'-'}</td>
                                <td onClick={(e)=>listItem.status===4&&listItem.reason?this.previewHandle(e,listItem.id):null}>{statusMap[listItem.status]}
                                    {
                                        this.state.previewShow&&this.state.previewId===listItem.id?
                                            <div ref={'preview'} className="preview" style={Object.assign({}, this.state.previewCss)}>
                                            <div className="text">{listItem.reason}</div>
                                        </div>:null
                                    }
                                </td>
                                <td>
                                    {
                                        listItem.status===0
                                            ?<div className="operateItem">
                                                <span className="acceptBtn" onClick={()=>{showModalHandle('accept',listItem.id)}}>审核通过</span>
                                                <span className="rejectBtn" onClick={()=>{showModalHandle('reject',listItem.id)}}>拒绝通过</span>
                                            </div>:''
                                    }
                                </td>
                            </tr>
                        )
                    }):null
                }
                </tbody>
            </table>
        </div>
    }


}
