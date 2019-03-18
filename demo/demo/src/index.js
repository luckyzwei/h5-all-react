import React from 'react';
import ReactDOM from 'react-dom';
import {Switch,Route,Router} from 'react-router'
import createBrowserHistory from 'history/createBrowserHistory'
import AdoptMain from './components/adoptComponent/AdoptMain';
import MainScope from './containers/MainScope';
import Error from './containers/Error'
import './index.css';

export const history = createBrowserHistory()

ReactDOM.render(
    <Router history={history}>
        <Switch>
            <Route path="/demo/error" component={Error}/>
            <Route path='/demo/adopt' component={AdoptMain}/>
            <Route path="/" component={MainScope}/>
        </Switch>
    </Router>, document.getElementById('root'));
