import React,{Component} from 'react'
import DataCircle from '../shareComponent/DataCircle'
export default class DataItem extends Component {
    render(){
        const {group_name,group_mem_counts,join_group_counts,exit_group_counts,speaker_counts} = this.props.data
        return (
            <div className="dataItem data-master">
                <div className="header">
                    <span className='groupName textHide'>{group_name}</span>
                </div>
                <div className="detail">
                    <div className="row">
                        <div className="left">群数据</div>
                        <div className="center">
                            <div className="svgBox">
                                <DataCircle 
                                    value={group_mem_counts?group_mem_counts:'0'}
                                />
                                <span className='memberNum'>{group_mem_counts?group_mem_counts:'0'}</span>
                            </div>
                            <p className='memberTitle'>群总人数</p>
                        </div>
                        <div className="right">
                            <p className='number'>进群人数：<span style={{color:'#55A0FF'}}>{join_group_counts?join_group_counts:'0'}</span></p>
                            <p className='number'>退群人数：<span style={{color:'#F75A5A'}}>{exit_group_counts?exit_group_counts:'0'}</span></p>
                            <p className='number'>发言人数：<span style={{color:'#55A0FF'}}>{speaker_counts?speaker_counts:'0'}</span></p>
                        </div>
                    </div>
                </div>
            </div>

        )
    }
}