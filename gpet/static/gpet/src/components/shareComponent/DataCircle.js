import React, {Component} from 'react'
export default class DataCircle extends Component {
constructor(props) {
    super(props)
    this.state = {
        percent : 350
    }
}
componentDidMount() {
    setTimeout(() => {
        this.setState({
            percent: 350-350*(this.props.value/500)
        })
    }, 100)
}
render() {
    const {percent} = this.state
    return (
        <div  className='dataCircleBox'>
            <svg width='100%' height='100%'>
                <defs>
                <linearGradient id="grad1" x1="100%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" style={{stopColor : '#67CCA6',stopOpacity:1}} />
                    <stop offset="60%" style={{stopColor:'#53A0FE',stopOpacity:1}}/>
                    <stop offset="100%" style={{stopColor:'#58A7F8',stopOpacity:1}}/>
                </linearGradient>
                </defs>
                <circle fill="none" stroke="#e9ebee" strokeWidth="10" strokeMiterlimit="1" cx="61" cy="61" r="56"/>
                <circle className="animate-item" style = {{transition: 'stroke-dashoffset 1s ease'}} fill="none"
                        stroke="#55A0FF" strokeWidth="10" strokeMiterlimit="1" cx="62" cy="62" r="55"  strokeDasharray="350 1000"
                        strokeDashoffset={percent} strokeLinecap="round" transform="rotate(-88 61 61)"></circle>
            </svg>
        </div>
    )
}
}