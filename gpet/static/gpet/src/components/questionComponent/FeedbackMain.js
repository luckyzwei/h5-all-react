import React, {Component} from 'react'
import SelectBox from '../shareComponent/SelectBox'
import SelectPet from './SelectPet'
import SelectGroup from './SelectGroup'
import SelectDes from './SelectDes'
import QuestionModal from './QuestionModal'
import {problems_back, push_problems_back} from '../../funStore/CommonPort'
import {tongji} from '../../constants/TrackEvent'
export default class FeedbackMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            problemCategorys: [],
            problemCategoryTilte: [],
            problemSelect: null,
            params: {
                //         problem_catgory:问题id,
                //         robot_id,
                //         group_name,
                //         description：描述
            },
            buttonBlock: false,
            problemFlag: true,
            robotFlag: true,
            groupFlag: true,
            desFlag: true,
            submitFlag: false,
            windowHeight: 0,
            buttonFlag: true
        }
        this.setparamsHandle = this.setparamsHandle.bind(this)
        this.submitHandle = this.submitHandle.bind(this)
        this.verifyHandle = this.verifyHandle.bind(this)
        this.hide = this.hide.bind(this)
        this.resizeHandle = this.resizeHandle.bind(this)
    }

    componentDidMount() {
        // 问题初始化
        problems_back().then(res => {
            if (res.code === 1200) {
                this.setState({
                    problemCategorys: res.data ? res.data : [],
                    problemCategoryTilte: res.data ? res.data.map(item => item.title) : []
                })
            }
        })
        // 检测弹窗弹起事件
        this.setState({
            windowHeight: window.innerHeight
        })
        window.addEventListener('resize', this.resizeHandle)
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.resizeHandle)
    }

    resizeHandle() {
        const {windowHeight} = this.state
        const currentHeight = window.innerHeight
        if (currentHeight < windowHeight) {
            this.setState({
                buttonFlag: false
            })
        } else {
            this.setState({
                buttonFlag: true
            })
        }
    }

    setparamsHandle(name, value) {
        let {params} = this.state
        if (name === 'problem_catgory') {
            let params = {}
            params[name] = value.id
            this.setState({
                params: params,
                problemSelect: value
            })
        } else {
            params[name] = value
            this.setState({
                params: params
            })
        }
    }

    submitHandle() {
        const {params, buttonBlock} = this.state
        if (buttonBlock) return
        if (!this.verifyHandle()) return
        this.setState({buttonBlock: true})
        push_problems_back(params).then(resData => {
            this.setState({buttonBlock: false})
            if (resData.code === 1200) {
                this.setState({submitFlag: true})
            }
        })
        tongji('feedback_questionSubmit')
    }

    verifyHandle() {
        const {params, problemSelect} = this.state
        let verifyArray = {
            2: ['problem_catgory', 'robot_id'],
            3: ['problem_catgory', 'robot_id', 'group_name'],
            4: ['problem_catgory'],
            5: ['problem_catgory', 'description']
        }
        this.setState({
            problemFlag: true,
            robotFlag: true,
            groupFlag: true,
            desFlag: true
        })
        let verifyResult = true
        verifyArray[problemSelect.type].forEach(item => {
            if (params[item] === '' || params[item] === undefined) {
                verifyResult = false
                switch (item) {
                    case 'problem_catgory':
                        this.setState({problemFlag: false})
                        break;
                    case 'robot_id':
                        this.setState({robotFlag: false})
                        break;
                    case 'group_name':
                        this.setState({groupFlag: false})
                        break;
                    case 'description':
                        this.setState({desFlag: false})
                        break;
                    default:
                        break;
                }
            }
        })
        return verifyResult
    }

    hide() {
        this.setState({submitFlag: false})
        this.props.history.push('/grouppet/home')
    }

    render() {
        const {problemCategorys, problemCategoryTilte, problemSelect, params, problemFlag, robotFlag, groupFlag, desFlag, submitFlag, buttonFlag} = this.state
        return (
            <div className='gp-container' style={{width: '100%', height: '100%'}}>
                <div className="feedback-wrapper">
                    <div className="title"/>
                    <div className='feedback-content'>
                        <SelectBox
                            selectLabel={''}
                            selectOption={problemCategoryTilte}
                            paramName={'problem_catgory'}
                            paramValue={problemCategorys}
                            setparamsHandle={this.setparamsHandle}
                            verify={problemFlag}
                        />
                        {
                            problemSelect && (problemSelect.type === 2 || problemSelect.type === 3)
                                ? <SelectPet
                                    setparamsHandle={this.setparamsHandle}
                                    robotFlag={robotFlag}
                                    clear={params.robot_id === undefined}
                                />
                                : ''
                        }
                        {
                            problemSelect && problemSelect.type === 3
                                ? <SelectGroup
                                    setparamsHandle={this.setparamsHandle}
                                    groupFlag={groupFlag}
                                    value={params.group_name}
                                /> : ''
                        }
                        {
                            problemSelect && (problemSelect.type === 2 || problemSelect.type === 3 || problemSelect.type === 5)
                                ? <SelectDes
                                    required={problemSelect.type === 5}
                                    setparamsHandle={this.setparamsHandle}
                                    desFlag={desFlag}
                                    value={params.description}
                                />
                                : ''
                        }
                        {buttonFlag ? <div className="saveBtn submitBtn" onClick={this.submitHandle}>提交</div> : ''}
                        {submitFlag ? <QuestionModal hide={this.hide}/> : ''}
                    </div>
                </div>
            </div>
        )
    }
}