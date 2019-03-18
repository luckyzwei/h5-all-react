import React,{Component} from 'react'
import {sendEvent, strLenIndex} from '../../funStore/CommonFun'

export const SpanKey = ({data,deleteKeyword,index})=>{
    return <div className='keyword' onClick={(e)=>deleteKeyword(data,index,e)}>
        <span className='name'>{data}</span>
        <span className='ic_key_delete'/>
    </div>
}

export default class AddKeyWord extends Component {
    constructor(props) {
        super(props)
        this.state={
            value:'',

        }
    }

    handleInput=(e)=>{
        this.setState({
            value:e.target.value
        })
    }

    handleBlur=()=> {
        let  flag = true
        const {value} = this.state
        this.props.keywords.forEach(item=>{
            if(item===value){
                flag = false
                sendEvent("messages", {msg:'关键词重复啦！', status: 200})
                return
            }
        })
        if(!flag) return
        let currentKeyword = value.slice(0,strLenIndex(value,11)) //截取10个字节
        if(value!==''){
            this.setState({
                value: ''
            }, () => {
                this.props.setHandleParams(currentKeyword, 2)
            })
        }
    }


    handleKewDown=(e)=> {
        if (e.keyCode === 13)
            this.handleBlur()
    }

    showInput=()=>{
        if (this.props.keywords.length<3) {
            this.refs.keywordInput.focus();
        }
    }


    render (){
        const {value} =this.state
        const {keywords,deleteKeyword} = this.props
        return (
            <div className='inputkeyWord' onClick={this.showInput}>
                {
                    keywords.length>0&&keywords.length<=3?
                        keywords.map((v,i)=>(
                            <SpanKey data={v} key={i} index={i} deleteKeyword={deleteKeyword}/>
                        ))
                        :null
                }

                {
                    keywords.length<3?
                        <input type="text" placeholder='输入关键词' value={value} ref={'keywordInput'}
                               onChange={this.handleInput}
                               onBlur={this.handleBlur}
                               onKeyDown={this.handleKewDown}
                        />
                        :null
                }
                <div className='wordlimit'>{keywords.length}/3</div>
            </div>
        )
    }

}