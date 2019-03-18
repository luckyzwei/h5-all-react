import React,{Component} from 'react'

export default class InfoBox extends Component {
    render(){
        const {content} =this.props
        return (
            <div className="infoBox">
                <span className="info-icon"/>
                <span className="info">消息：</span>
                <div className="outer">
                    <div className="textSlide">
                        <div className="msg">{content}</div>
                        <div className="msg">{content}</div>
                    </div>
                </div>
            </div>
        )
    }
}
