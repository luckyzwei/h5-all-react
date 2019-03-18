import React from 'react';
import ReactDOM from 'react-dom';
import {Switch,Route,Router} from 'react-router'
import createBrowserHistory from 'history/createBrowserHistory'
import $ from 'jquery'
import {API_URL} from "./constants/Api";
import {API_PATH} from './constants/OriginName'
import {WXsharing} from './funStore/WXsharing'
import Loadable from 'react-loadable'
import LoadingAnimationA from './components/shareComponent/LoadingAnimationA'
import './index.scss'

const Loading = () => <div className='verticalCenter'><LoadingAnimationA/></div>
const AdoptScope = Loadable({loader: () => import('./containers/AdoptScope'), loading: () => <Loading/>,});
const MainScope = Loadable({loader: () => import('./containers/MainScope'), loading: () => <Loading/>,});
const OfflineScope = Loadable({loader: () => import('./containers/OfflineScope'), loading: () => <Loading/>,});
const ErrorNoauth = Loadable({loader: () => import('./containers/ErrorNoauth'), loading: () => <Loading/>,});
const Error = Loadable({loader: () => import('./containers/Error'), loading: () => <Loading/>,});

export const history = createBrowserHistory()

// 系统状态判断 status 1代表服务正常 2代表服务维护 同步请求
$.ajax({
    type:'get',
    async: false,
    url: API_PATH+API_URL.appStatus,
    success: function(res){
        if (res.code === 1200 && res.data.status === 2) {
            history.replace('/grouppet/offline?time=' + encodeURI(res.data.upGradeEndTime))
        }
    }
})

ReactDOM.render(
    <Router history={history}>
        <Switch>
            <Route path='/grouppet/offline' component={OfflineScope}/>
            <Route path="/grouppet/error" component={Error}/>
            <Route path="/grouppet/noauth" component={ErrorNoauth}/>
            <Route path="/grouppet/adopt" component={AdoptScope}/>
            <Route path="/" component={MainScope}/>
        </Switch>
    </Router>,
    document.getElementById('root')
);

// 微信分享
WXsharing()
