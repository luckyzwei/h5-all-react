import React, {Component} from 'react'
import './selectBox.scss'

export default class SelectBox extends Component {
    constructor() {
        super();
        this.state = {
            showOption: false,
            currentId: -1,
            selectTitle: "请选择类型",
            ifSelect: false
        }
    }

    showMoreOption() {
        this.setState({
            showOption: !this.state.showOption
        })
    }

    selectedOption(index, sentList, name, value) {
        this.setState({
            currentId: index,
            selectTitle: sentList,
            showOption: !this.state.showOption,
            ifSelect: true
        })
        if (this.props.changeClear) {
            this.props.changeClear()
        }
        if (this.props.setParamasHandle) {
            this.props.setParamasHandle(name, value, sentList, index)
        }
    }

    hideOption() {
        this.setState({
            showOption: false
        })
    }

    componentWillMount() {
        if (this.props.placeholder) {
            this.setState({
                selectTitle: this.props.placeholder
            })
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.clear) {
            this.setState({
                currentId: -1,
                selectTitle: this.props.placeholder ? this.props.placeholder : "请选择类型",
                ifSelect: false
            })
        }
    }

    render() {
        let {showOption, currentId, selectTitle, ifSelect} = this.state
        let {selectLabel, selectOption, paramaName, paramDefault, paramaValue, width, all, verify, iptColor, disableBackground} = this.props
        const widthStyle = width !== undefined ? {width: width} : {}
        const id = this.props.id === undefined || this.props.id === '' ? '' : this.props.id;
        const _currentId = paramDefault !== undefined && currentId === -1 ? paramDefault.id : currentId
        return (
            <div className='selectWrapper' onBlur={this.hideOption.bind(this)} tabIndex={1}>
                <div className="selectLabel">{selectLabel}</div>
                <div className="selectBox" style={widthStyle}>
                    <div className="selectOption" id={id} onClick={this.showMoreOption.bind(this)}
                         style={Object.assign({}, {border: verify ? '1px solid red' : showOption ? "1px solid #58A7F8" : iptColor ? iptColor : "1px solid transparent"}, widthStyle, {backgroundColor: disableBackground ? disableBackground : ''})}>
                        <em className={!ifSelect && paramDefault === undefined ? "unselectedTip" : "selectTip"}>
                            {!ifSelect && paramDefault !== undefined ? paramDefault.name : selectTitle}
                        </em>
                        <span className={showOption ? "selectArrow selIcon" : "selIcon"}/>
                    </div>
                    <div className="optionUl" style={Object.assign({}, {
                        display: showOption ? "block" : "none",
                        transition: 'all .4s'
                    }, widthStyle)}>
                        <ul>
                            <li style={{display: all ? 'block' : 'none'}}
                                className={_currentId === null ? "selected" : ""}
                                onClick={this.selectedOption.bind(this, null, '全部', paramaName, null)}>全部
                            </li>
                            {selectOption.map((data, index) => {
                                return <li
                                    key={index}
                                    className={_currentId === index ? "selected" : ""}
                                    onClick={this.selectedOption.bind(this, index, data, paramaName, paramaValue[index])}
                                > {data} </li>
                            })}
                        </ul>
                    </div>
                </div>
            </div>
        )
    }
}

