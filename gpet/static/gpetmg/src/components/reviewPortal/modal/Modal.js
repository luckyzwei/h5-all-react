import React,{Component} from 'react'

const textMap = {
    'accept': '你确定审核通过？',
    'reject': '你确定拒绝审核？',
    'batchAccept': '你确定批量审核通过？',
    'batchReject': '你确定批量拒绝审核？'
}

export default class Modal extends Component {
    constructor(props){
        super(props)
        this.confirmHandle = this.confirmHandle.bind(this)
    }
    confirmHandle(){
        const {status,reviewHandle,checkId,batchReviewHandle} = this.props
        if(status==='accept'){
            reviewHandle(checkId,1)
        }else if(status==='reject'){
            reviewHandle(checkId,2)
        }else if(status==='batchAccept'){
            batchReviewHandle(1)
        }else{
            batchReviewHandle(2)
        }
    }
    render(){
        const {status,hideModalHandle,total} = this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox reviewModal">
                    <p style={{padding:status==='batchAccept'||status==='batchReject'?'40px':'50px'}}>
                        {status==='batchAccept'||status==='batchReject'?<p style={{padding: 0,marginBottom:'10px'}}>总金额：<span style={{color:'#F75A5A'}}>{total}</span></p>:''}
                        {textMap[status]}
                    </p>
                    <div className="buttonArea">
                        <div className="cancelBtn" onClick={hideModalHandle}>取消</div>
                        <div className="confirmBtn" onClick={this.confirmHandle}>确定</div>
                    </div>
                    <div className="icon-background closeBtn" onClick={hideModalHandle}/>
                </div>
            </div>
        )
    }
}