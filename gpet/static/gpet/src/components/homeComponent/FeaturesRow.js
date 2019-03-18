import React ,{Component} from 'react'
import {tongji} from '../../constants/TrackEvent'

export default class FeaturesRow extends Component{
    handleGoto=(goLink,text,event)=>{
        if(goLink!=='')
            this.props.history.push(goLink)
            tongji('click_'+event)
    }
    render(){
        const {featuresData} =this.props
        return (<div className="row">
            {
                featuresData.map((item,index)=>{
                    return  <div className='column' key={index} onClick={()=>this.handleGoto(item.goLink,item.text,item.event)}>
                        <span className='home_icon' style={{backgroundPosition:item.imgSrc}}/>
                        <span>{item.text}</span>
                    </div>
                })
            }
        </div>)
    }
}

