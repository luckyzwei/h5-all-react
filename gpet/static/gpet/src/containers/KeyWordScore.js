import React, {Component} from 'react'
import {Switch, Route} from 'react-router'
import Loadable from 'react-loadable'
import LoadingAnimationA from '../components/shareComponent/LoadingAnimationA'
import MsgEmpty from '../components/shareComponent/MsgEmpty'//没有群主群
import {tongji} from '../constants/TrackEvent'
import {OwnerIsGroup, Keywords} from "../funStore/CommonPort";
const Loading = () => <div className='verticalCenter'><LoadingAnimationA/></div>
const KeyWordMain = Loadable({loader: () => import('../components/keyWordComponent/KeyWordMain'), loading: () => <Loading/>,});
const KeyWordDetails = Loadable({loader: () => import('../components/keyWordComponent/KeyWordDetails'), loading: () => <Loading/>,});

export default class KeyWordScore extends Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            isHasGroup: true,//是否有导群
            keywordData: [],

        }
    }

    componentDidMount() {
        //1.判断用户是否有群主群
        let self = this
        OwnerIsGroup().then(res => {
            if (res.code === 1200 && res.data) {
                self.getKeywordData()
            } else {
                self.setState({
                    isHasGroup: false,
                    loading: false
                })
            }
        })
    }

    getKeywordData = () => {
        Keywords().then(res => {
            this.setState({
                loading: false,
                keywordData: res.data && res.data.length > 0 ? res.data : []
            })
        })
    }

    backTask = (id) => {
        this.setState({
            keywordData: this.state.keywordData.filter(item => item.batch_id !== id)
        }, this.getKeywordData)

    }

    goDetails = (id) => {
        this.props.history.push('/grouppet/keyword/creatkeyword/' + id)
        tongji(id === '' ? 'keyword_add':'keyword_edit')
    }

    render() {
        const {loading, isHasGroup, keywordData} = this.state
        const propsData = {
            keywordData: keywordData,
            backTask: this.backTask,
            goDetails: this.goDetails,
            getKeywordData: this.getKeywordData,
        }
        return (
            loading ? <LoadingAnimationA/> :
                isHasGroup ?
                    <Switch>
                        <Route path="/grouppet/keyword/keywordlist"
                               render={props => (<KeyWordMain  {...props} {...propsData}/>)}/>
                        <Route path="/grouppet/keyword/creatkeyword/:id?"
                               render={props => (<KeyWordDetails {...props} {...propsData}/>)}/>
                    </Switch>
                    : <MsgEmpty type={5}/>
        )
    }
}
