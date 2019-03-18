import React,{Component} from 'react'

export default class ErrorNoauth extends Component {
    componentDidMount(){
        document.title='404'
    }
    render(){
        return (
            <div style={{height:'100%'}}>
                <div className='gp-container'>
                    <div className="noauth-wrapper">
                        <p>对不起，你的账号因为违反用户<br/>协议而被封停，故无法登录。</p>
                        <div className="img"/>
                    </div>
                </div>
            </div>
        )
    }
}