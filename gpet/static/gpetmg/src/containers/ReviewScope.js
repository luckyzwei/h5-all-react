import React ,{Component}from 'react'
import ReviewMain from '../components/reviewPortal/ReviewMain'
export default class ReviewScope extends Component{
    render(){
        return(
            <div className="wrapper-container">
                <ReviewMain history={this.props.history}/>
            </div>
        )
    }
}