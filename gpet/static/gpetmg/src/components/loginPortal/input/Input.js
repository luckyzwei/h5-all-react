import React,{Component} from 'react'
import './input.scss'

export default class Input extends Component {
    inputHandle = (e) => {
        this.props.inputHandle(this.props.paramName,e.target.value)
    }
    render(){
        const {propsStyle,tip,placeholder,type,verifty,value} = this.props
        return (
            <div className="inputBox">
                <div className="tip">{verifty?tip:''}</div>
                <input type={type} placeholder={placeholder} onChange={this.inputHandle} defaultValue={value}/>
                <div className={propsStyle}/>
            </div>
        )
    }
}