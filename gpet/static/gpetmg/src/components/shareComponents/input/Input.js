import React ,{Component}from 'react'
import './input.scss'
export default class Input extends Component{
    render(){
        const {maxLength,label,name,placeholder,handleChange} = this.props
        return(
            <div className="selectInput">
                {
                    label? <div className="selectLabel">{label}</div>:null
                }
                <input type='text' maxLength={maxLength?maxLength:null} className="titleInput" autoComplete='off'
                       name={name} placeholder={placeholder}
                       onChange={(e)=>{handleChange(e.target.name,e.target.value)}}/>
            </div>
        )
    }
}