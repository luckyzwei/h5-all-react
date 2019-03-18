import React,{Component} from 'react'
import './topNavi.scss'
export default class TopNavi extends Component{
    logoutHandle = ()=>{
        localStorage.removeItem('gpet_mg_name')
        localStorage.removeItem('gpet_mg_psd')
        this.props.history.push('/gpetmg/login')
    }
    render(){
        return (
            <div className='top-header'>
                <div className="logout" onClick={this.logoutHandle}>
                    <span className="icon"/>
                    退出
                </div>
            </div>
        )
    }
}