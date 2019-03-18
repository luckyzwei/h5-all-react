import React, {Component} from 'react'

class GoHomeScope extends Component {
    goHomeHandle=()=>{
        this.props.history.push('/grouppet/home')
    }
    render() {
        return (<div className='goHome' onClick={this.goHomeHandle}/>)
    }
}

export default GoHomeScope