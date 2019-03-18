import React,{Component} from 'react'

export default class SwitchAlt extends Component {
    render(){
        const {switchStatus,hideHandle,changeSwitch,handleChangeAntme} =this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox writeBox openAnt">
                    <div className="title">
                        <div>每条群内@你的消息，机器人都可以主动通知你</div>
                        <div className='iconBox'>
                            <span className={`${switchStatus?'selectedIcon':'selectedIcon unselected'}`}
                                  onClick={changeSwitch}/>
                            开启自动提醒
                        </div>
                    </div>
                    <div className='btnBox' onClick={handleChangeAntme}>
                        <button className='confrimBtn'>知道啦！</button>
                    </div>
                    <div className='icon-cross closeBtn' onClick={hideHandle}/>
                </div>
            </div>
        )
    }
}