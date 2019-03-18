import React,{Component} from 'react'

export default class SelectDes extends Component {
    constructor(props){
        super(props)
        this.changeHandle = this.changeHandle.bind(this)
    }
    changeHandle(e){
        this.props.setparamsHandle('description',e.target.value)
    }
    onBlur=()=>{
        window.scroll(0,0)
    }
    render(){
        const {required,desFlag,value} = this.props
        return (
            <div className="selectWrapper">
                <textarea placeholder={required?'备注说明':'备注说明（选填）'} value={value?value:''}
                          onChange={this.changeHandle} style={{border:desFlag?'1px solid #979797':'1px solid red'}}
                          onBlur={this.onBlur}
                />
            </div>
        )
    }
}