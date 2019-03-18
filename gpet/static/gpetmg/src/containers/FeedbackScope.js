import React ,{Component}from 'react'
import FeedbackMain from '../components/feedbackPortal/FeedbackMain'
export default class FeedbackScope extends Component{
    render(){
        return(
            <div className="wrapper-container">
                <FeedbackMain history={this.props.history}/>
            </div>
        )
    }
}