import React,{Component} from 'react'

export default class SelectGroup extends Component {
    constructor(props){
        super(props)
        this.state = {}
        this.changeHandle = this.changeHandle.bind(this)
    }
    changeHandle(e){
        this.props.setparamsHandle('group_name',e.target.value)
    }
    onBlur=()=>{
        window.scroll(0,0)
    }
    render(){
        const {groupFlag,value} = this.props
        return (
            <div className="selectWrapper">
                <input className="selectOption" type="text" placeholder='填写完整群名' value={value?value:''}
                       onChange={this.changeHandle}
                       onBlur={this.onBlur}
                       style={{border:groupFlag?'1px solid #979797':'1px solid red'}}/>
            </div>
        )
    }
}