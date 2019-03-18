import React,{Component} from 'react'
import {TextCountRange} from '../../funStore/CommonFun'
import ButtonLoading from '../shareComponent/ButtonLoading'
export default class ChRobotName extends Component {
    state={
        robot_name:this.props.checkItem.robot_name!=null?this.props.checkItem.robot_name:''
    }
    handleInput=(e)=>{
        let value = e.target.value
        this.props.sensitTrue()
        if(TextCountRange(value)<=16){
            this.setState({
                robot_name:value
            })
        }
    }
    render(){
        const {robot_name} =this.state
        const {hideHandle,confirmHandle,sensitCheck,changeName} =this.props
        return (
            <div className="modalWrapper">
                <div className="modalBox chRobotname">
                    <div className='title'>修改群昵称</div>
                    <div className='inputBox' style={{position:'relative'}}>
                        <input type="text" className={`robot-input ${!sensitCheck?'error':''}`} value={robot_name} onChange={(e)=>this.handleInput(e)}/>
                        {!sensitCheck?<p className='robot-error'>你输入的内容不符合内容安全标准</p>:null}
                    </div>
                    <div className="btnBox">
                        {
                            !changeName?<button className='robot-btn' onClick={()=>{confirmHandle(robot_name)}}>确认</button>
                                :<div className='robot-btn' style={{margin:'50px auto 0'}}>
                                    <ButtonLoading text={'修改中'} color={'#fff'}/>
                                </div>
                        }

                    </div>
                    <div className='icon-cross closeBtn' onClick={hideHandle}/>
                </div>
            </div>
        )
    }
}