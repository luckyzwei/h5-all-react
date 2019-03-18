import React,{Component} from 'react'
import SelectBox from '../shareComponent/SelectBox'
import {select_pet} from '../../funStore/CommonPort'
export default class SelectPet extends Component {
    constructor(props){
        super(props)
        this.state = {
            robotList:[]
        }
    }
    componentDidMount(){
        select_pet().then(resData => {
           if(resData.code===null||resData.code===1200){
               this.setState({
                   robotList: resData.data
               })
           }
        })
    }
    render(){
        const {robotList} = this.state
        const {setparamsHandle,robotFlag,clear} = this.props
        return (
            <SelectBox
                selectTitle={'选择宠物和微信号'}
                selectLabel={''}
                selectOption={robotList.map(item => {return `${item.name} 微信号：${item.wechat_no}`})}
                paramName={'robot_id'}
                paramValue={robotList.map(item => item.id)}
                setparamsHandle={setparamsHandle}
                verify={robotFlag}
                clear={clear}
            />
        )
    }
}