import React, {Component} from "react"

export default class SelectBox extends Component {
    constructor() {
        super();
        this.state = {
            showOption: false,
            currentId: -1,
            selectTitle: "请选择你的问题",
            ifSelect: false
        }
    }

    componentDidMount() {
        if (this.props.selectTitle) {
            this.setState({
                selectTitle: this.props.selectTitle
            })
        }
    }

    showMoreOption() {
        this.setState({
            showOption: !this.state.showOption
        })
    }

    selectedOption(id, sentList, name, value) {
        this.setState({
            currentId: id,
            selectTitle: sentList,
            showOption: !this.state.showOption,
            ifSelect: true
        })
        this.props.setparamsHandle(name, value)
    }

    hideOption() {
        this.setState({
            showOption: false
        })
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.clear) {
            this.setState({
                currentId: -1,
                selectTitle: this.props.selectTitle ? this.props.selectTitle : '请选择你的问题',
                ifSelect: false
            })
        }
    }

    render() {
        let {showOption, currentId, selectTitle, ifSelect} = this.state
        let {
            selectLabel, selectOption, paramName, paramDefault,
            paramValue, width, all, verify
        } = this.props
        const widthStyle = width !== undefined ? {width: width} : {}
        const id = this.props.id === undefined || this.props.id === '' ? '' : this.props.id;
        const _currentId = paramDefault !== undefined && currentId === -1 ? paramDefault.id : currentId
        return (
            <div className='selectWrapper' onBlur={this.hideOption.bind(this)} tabIndex={1}>
                <div className="selectLabel">{selectLabel}</div>
                <div className="selectBox" style={widthStyle}>
                    <div className="selectOption" id={id} onClick={this.showMoreOption.bind(this)}
                         style={Object.assign({}, {border: !verify ? '1px solid red' : showOption ? "1px solid #979797" : "1px solid #979797"}, widthStyle)}>
                        <em className={!ifSelect && paramDefault === undefined ? "unselecedTip" : "selectTip"}>{!ifSelect && paramDefault !== undefined ? paramDefault.name : selectTitle}</em>
                        <span className={showOption ? "selectArrow selIcon" : "selIcon"}/>
                    </div>
                    {/*<div className="optionUl" style={Object.assign({}, {display: showOption ? "block" : "none"}, widthStyle)}>*/}
                    <div className="optionUl" style={Object.assign({}, {maxHeight: showOption ? '467px' : "0"}, widthStyle)}>
                        <ul>
                            <li style={{display: all ? 'block' : 'none'}}
                                className={_currentId === null ? "selected" : ""}
                                onClick={this.selectedOption.bind(this, null, '全部', paramName, null)}>全部
                            </li>
                            {selectOption.map((data, id) => {
                                return <li
                                    key={id}
                                    className={_currentId === id ? "selected" : ""}
                                    onClick={this.selectedOption.bind(this, id, data, paramName, paramValue[id])}
                                > {data} </li>
                            })}
                        </ul>
                    </div>
                </div>
            </div>
        )
    }
}