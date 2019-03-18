
import React,{Component} from 'react'
import './sidenavi.scss'
let naviInfo = [

    {
        id: '1',
        "code": "review",
        "name": "打款审核",
        "orderSeq": 1,
        "target": "/gpetmg/review",
        "status": 1,
        "selected": null,
        "children": null
    }, {
        id: '2',
        "code": "feedback",
        "name": "问题反馈",
        "orderSeq": 4,
        "target": "/gpetmg/feedback",
        "handleRight": "HR_CUSTOMIZED_ROBOT;HR_TRIAL_GROUP",
        "status": 1,
        "selected": null,
        "children": null
    }
]

const dataMap = {
    home: 'icon-home',
    delivery: 'icon-delivery',
    dashboard: 'icon-data',
    finance: 'icon-wealth',
    account: 'icon-account'
}
const SubNavi = ({ navi, subNavi, expand, history }) => {
    return (
        <div className='subNavi' style={{ height: expand ? subNavi.length * 36 + 'px' : 0 }}>
            {
                subNavi.map((v, i) => <div key={i}
                                           className={`subNaviItem ${history.location.pathname.includes(v.target)?'active':''}`}
                                           onClick={() => { history.push(navi.target + v.target) }}>{v.name}</div>)
            }
        </div>
    )
}
class NaviItem extends Component {
    clickHandle = () => {
        const { navi, expandHandle, history } = this.props
        if (navi.children == null) {
            history.push(navi.target)
        }
        expandHandle(navi.id)
    }
    render() {
        const { navi, history } = this.props
        const activeFlag = history.location.pathname.includes(navi.target)
        return (
            <div className={`naviItem ${navi.children?'secondNavi':''}`}>
                <div className={`naviText ${activeFlag?'active':''} ${navi.selected?'expand':''}`} onClick={this.clickHandle}>
                    <span className={`navi-icon ${dataMap[navi.code]}`}/>
                    <span>{navi.name}</span>
                </div>
                {navi.children ? <SubNavi navi={navi} subNavi={navi.children} expand={navi.selected} history={history} /> : ''}
            </div>
        )
    }
}

export default class SideNavi extends Component{
    constructor(props){
        super(props)
        this.state = {
            naviInfo: naviInfo
        }
    }
    componentDidMount() {
        const pathname = this.props.history.location.pathname

        let { naviInfo } = this.state
        naviInfo = naviInfo.map((v, i) => {
            return {
                ...v,
                selected: pathname.includes(v.target)
            }
        })
        this.setState({ naviInfo })
    }
    expandHandle = (id) => {
        let { naviInfo } = this.state
        naviInfo = naviInfo.map((v, i) => {
            return v.id === id ? {
                ...v,
                selected: !v.selected
            } : {
                ...v,
                selected: false
            }
        })
        this.setState({ naviInfo })

    }
    render(){
        const {naviInfo} =this.state
        const {history} =this.props
        return <div className='naviBox'>
            <div className="avatar">
                <img src="http://img.zcool.cn/community/01ee0d5544f1380000019ae9895b3f.jpg@1280w_1l_2o_100sh.jpg" alt="" />
                <p>群宠管理系统</p>
            </div>
            <div className="navi">
                {
                    naviInfo.map((navi, i) => {
                        return <NaviItem key={i} navi={navi} expandHandle={this.expandHandle} history={history} />
                    })
                }
            </div>
        </div>
    }
}