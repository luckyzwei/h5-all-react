import React, {Component} from 'react'

function createMarkup(text) {
    return {__html: text};
}

const Answer = ({text}) => {
    return <div className="text" dangerouslySetInnerHTML={createMarkup(text)}/>
}

export default class QurestionItem extends Component {
    constructor(props) {
        super(props)
        this.state = {
            height: 102,
            deltaHeight: 0
        }
        this.expandHandle = this.expandHandle.bind(this)
    }

    componentDidMount() {
        this.setState({
            deltaHeight: this.refs.detail.offsetHeight
        })
    }

    expandHandle(e) {
        e.stopPropagation()
        this.props.checkHandle(this.props.index)
    }

    render() {
        const {height, deltaHeight} = this.state
        const {index, checkIndex, item} = this.props
        let styleHeight = {
            maxHeight: item.isExpand && checkIndex === index ? height + deltaHeight + 'px' : height + 'px',
            paddingBottom: item.isExpand && checkIndex === index ? '30px' : ''
        }
        return (
            <div className="item" ref="content" style={styleHeight}>
                <div className="question" onClick={this.expandHandle}>
                    <span className="text">{item.q}</span>
                    <span className={item.isExpand && checkIndex === index ? "downArrow up" : "downArrow"}/>
                </div>
                <div className="answer" ref="detail">
                    {
                        item.a.map((answer, index) => <Answer key={index} text={answer}/>)
                    }
                </div>
            </div>
        )
    }
}
