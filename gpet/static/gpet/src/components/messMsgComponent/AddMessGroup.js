import React, {Component} from 'react'

export default class AddMessGroup extends Component {
    constructor(props) {
        super(props)
        this.state = {
            selectedGroup: [],
            isSelectAll: false,
        }
    }

    componentDidMount() {
        this.setState({
            selectedGroup: this.props.paramsSelected.map(item => item)
        })
    }

    //选择群
    selectGroup = (itemId) => {
        let {selectedGroup} = this.state;
        let {groupList} = this.props
        let index = selectedGroup.indexOf(itemId);
        if (index >= 0) {
            selectedGroup.splice(index, 1);
        } else {
            selectedGroup.push(itemId);
        }
        this.setState({
            selectedGroup: selectedGroup,
            isSelectAll: selectedGroup.length === groupList.length
        });
    }

    // 全选
    checkAll = () => {
        const self = this;
        let {selectedGroup, isSelectAll} = self.state;
        let {groupList} = self.props
        if (!isSelectAll) {
            groupList.forEach(item => {
                let index = selectedGroup.indexOf(item.code);
                if (index === -1) {
                    selectedGroup.push(item.code);
                }
            });
        } else {
            selectedGroup = [];
        }
        self.setState({
            isSelectAll: !isSelectAll,
            selectedGroup: selectedGroup
        });
    }

    handleSubmit = () => {
        this.props.setHandleParams(this.state.selectedGroup, 0)
    }

    render() {
        const {selectedGroup, isSelectAll} = this.state;
        const {groupList} = this.props
        return (
            <div className='modalWrapper' ref='modalWrapper' onClick={this.props.closeSelectGroup}
                 style={{zIndex: '19999'}}>
                <div className='addMessGroup-view' onClick={(e) => {
                    e.stopPropagation()
                }}>
                    <div className='groupItemList'>
                        {
                            groupList.length > 0 ? groupList.map((item, index) => {
                                return <div key={'gl-' + index}
                                            className={`groupItem ${selectedGroup.indexOf(item.code) > -1 || isSelectAll ? 'checked' : ''}`}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                this.selectGroup(item.code)
                                            }}>
                                    <div className="bar"/>
                                    <div className="groupInfo">
                                        <div className="groupName">{item.name}</div>
                                        <div className="time">导入时间：{item.create_date}</div>
                                    </div>
                                    <div className="checkIcon"/>
                                </div>
                            }) : null
                        }
                    </div>

                    <div className="selectBox">
                        <div className="left">
                            <div className="checkAll" onClick={(e) => {
                                e.stopPropagation();
                                this.checkAll()
                            }}>
                                <div
                                    className={`checkIcon ${isSelectAll || selectedGroup.length === groupList.length ? 'checked' : ''}`}/>
                                <span>全选</span>
                            </div>
                        </div>
                        <div className="right button-blue" onClick={(e) => {
                            e.stopPropagation();
                            this.handleSubmit()
                        }}>确认
                        </div>
                    </div>

                </div>
            </div>
        )
    }
}