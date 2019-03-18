import React, {Component} from 'react'
import LoadingAnimationA from '../shareComponent/LoadingAnimationA'
import {Error1} from '../adoptComponent/AdoptError'
import {import_robot} from '../../funStore/CommonPort'
import {getCookie} from "../../funStore/CommonFun";
import AuthProvider from "../../funStore/AuthProvider";

export default class ImportMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            robotInfo: null,
            pageLoad: true,
            view: 'page'
        }
    }

    componentDidMount() {
        document.title = '导入群'
        let accessToken = getCookie('access_token',1*3600*1000)
        if(accessToken===null|| accessToken === 'null'){
            AuthProvider.onLogin(getCookie('union_id')).then(res => {
                this.getImportRobot()
            })
        }else{
            this.getImportRobot()
        }
    }

    getImportRobot=()=>{
        import_robot().then(resData => {
            //1200：正常,1404：用户不存在，1600:机器人数量不足
            if (resData.code === 1200) {
                this.setState({
                    robotInfo: resData.data,
                    pageLoad: false
                })
            } else if (resData.code === 1600 || resData.code === 1404) {
                this.setState({
                    view: 'error',
                    pageLoad: false
                })
            } else {
                this.setState({
                    view: 'error',
                    pageLoad: false
                })
            }
        })
    }

    render() {
        const {robotInfo, pageLoad, view} = this.state
        return (
            pageLoad ? <LoadingAnimationA/>
                : <div className='gp-container'>
                    {
                        view === 'page' ? <div className="import-wrapper">
                                <img src={robotInfo ? robotInfo.qr_code : ''} alt='' className='import_qrcode'/>
                            </div>
                            : <Error1/>
                    }
                </div>
        )
    }
}
