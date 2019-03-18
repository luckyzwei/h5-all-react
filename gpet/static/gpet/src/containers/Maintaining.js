import React, {Component} from 'react'
export default class Maintaining extends Component{
    componentDidMount(){
        document.title='正在维护'
    }
    render(){
        return(
            <div className='gp-container'>
                <div className="error-wrapper">
                    <p>此功能正在维护<br/>敬请期待</p>
                    <img className='img404' src={"/images/icon/pic_offline.png"} alt=""/>
                </div>
            </div>
        )
    }

}


