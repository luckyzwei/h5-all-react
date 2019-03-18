import React,{Component} from 'react'

export default class KnowMore extends Component {
    render(){
        const {hideHandle} =this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox writeBox openAnt">
                    <div className="title">
                        投放范围可以选择群内是否投放文章啦，如果关闭的话，点击收益也会没有哦！
                    </div>
                    <div className='btnBox' onClick={hideHandle}>
                        <button className='confrimBtn'>知道啦！</button>
                    </div>
                    <div className='icon-cross closeBtn' onClick={hideHandle}/>
                </div>
            </div>
        )
    }
}