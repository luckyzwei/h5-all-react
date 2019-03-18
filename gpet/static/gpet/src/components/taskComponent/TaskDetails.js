import React,{Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import PastDetails from './PastDetails'
import {task_detai} from '../../funStore/CommonPort'
export default class TaskDetails extends Component {
    constructor(props) {
        super(props)
        this.state={
            loading:true,
            data:[],
            id:''
        }
    }
    componentDidMount() {
        document.title = '群内投放'
        const {match} =this.props
        this.setState({
            id:match.params.id
        })
        this.getPastData(match.params.id)
    }

    //获取过去3天的信息
    getPastData=(id)=>{
        task_detai(id).then(res=>{
            this.setState({
                loading:false
            })
            if(res.code===1200)
                this.setState({
                    data:res.data
                })
        })
    }

    render(){
        const {loading,data} =this.state
        return  (
            loading
                ?<LoadingAnimationA/>
                :
                <div className='taskDetail-wrapper'>
                    <PastDetails  data={data}/>
                </div>

        )

    }
}
