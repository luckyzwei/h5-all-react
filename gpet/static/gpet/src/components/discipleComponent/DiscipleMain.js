import React,{Component} from 'react'
import DiscipleList from './DiscipleList'

export default class DiscipleMain extends Component {
    componentDidMount(){
        document.title = '徒弟徒孙'
    }
    render(){
        return (
            <div className='gp-container' style={{background:'#fff'}}>
                <DiscipleList />
            </div>
        )
    }
}