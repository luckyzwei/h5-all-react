import React,{Component} from 'react'
export default class ImgPreview extends Component {
    render(){
        return (
            <div className="modalWrapper" onTouchEnd={this.props.hidePreviewImg}>
                <div className="modalBox">
                    <img src={this.props.src} alt="" style={{width:'608px'}}/>
                </div>
            </div>
        )
    }
}