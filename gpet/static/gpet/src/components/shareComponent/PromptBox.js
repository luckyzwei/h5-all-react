import React,{Component} from 'react'
export default class PromptBox extends Component {

    render(){
        const {text,onClose,onConfrim} =this.props
        return <div className='modalWrapper'>
            <div className="modalBox new-promptBox">
                <div className='title'>
                    {text}
                </div>
                <div className='promptBtnBox'>
                    <span className='cancelBtn' onClick={onClose}>取消</span>
                    <span className='confrimBtn' onClick={onConfrim}>确定</span>
                </div>
            </div>
        </div>
    }
}