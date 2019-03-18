import React from 'react';
import ReactDOM from 'react-dom';
import {Switch,Route,Router} from 'react-router'
import createBrowserHistory from 'history/createBrowserHistory'
import Error from './containers/Error'
import Messages from './components/shareComponents/message/Messages'
import SideNavi from './components/sideNavi/SideNavi'
import TopNavi from './components/topNavi/TopNavi'
import LoginMain from './components/loginPortal/LoginMain'
import ReviewScope from "./containers/ReviewScope";//打款审核
import FeedbackScope from "./containers/FeedbackScope";
import {LOGIN_USER} from "./constants/OriginName";
import './index.scss';

export const history = createBrowserHistory()

const MainScope = ({ history }) => {
    let username = localStorage.getItem('gpet_mg_name')
    let password = localStorage.getItem('gpet_mg_psd')
    if(username!==LOGIN_USER.username||password!==LOGIN_USER.password){
        history.push('/gpetmg/login')
    }
    return (
        <div className="container">
            <div className="left"><SideNavi history={history} /></div>
            <div className="right">
                <div className="header"><TopNavi history={history} /></div>
                <div className="content">
                    <Switch>
                        <Route path='/gpetmg/review' component={ReviewScope} />
                        <Route path='/gpetmg/feedback' component={FeedbackScope} />
                    </Switch>
                </div>
                <Messages/>
            </div>
        </div>
    )
}

ReactDOM.render(
    <Router history={history}>
        <Switch>
            <Route path="/gpetmg/login" component={LoginMain} />
            <Route path="/gpetmg/error" component={Error} />
            <Route path="/gpetmg" component={MainScope} />
        </Switch>
    </Router>,
    document.getElementById('root')
);

