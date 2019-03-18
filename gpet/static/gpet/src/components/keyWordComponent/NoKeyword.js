import React,{Component} from 'react'
export default class NoKeyword extends Component {
    handleClickGoTo=()=>{
        this.props.history.push('/grouppet/keyword/creatkeyword')
    }

    render(){
        return <div className='new-containter'>
            <div className='sh-shareView'>
                <div className='shareView-info'>
                    <p>你暂时还未设置过关键词自动回复哦</p>
                    <p>赶快来试试吧</p>
                </div>
                <div className='shareView-img'>
                    <img src={'/images/icon/pic_kongzhuangtai.png'} alt="" />
                </div>
                <div className='shareView-type-btnBox' onClick={this.handleClickGoTo}>新增关键词</div>
            </div>
        </div>
    }

}

