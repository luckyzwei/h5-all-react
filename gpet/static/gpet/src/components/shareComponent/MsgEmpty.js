import React,{Component} from 'react'
import {history} from '../../index'
/**
 * //只有群主有权利操作
 * type
 * 1:pic_empty_@me @我
 * 2:pic_empty_data 群数据
 * 3:pic_empty_hi 入群欢迎语
 * 4:pic_empty_send 群发消息
 * 5:关键词
 * 6.标签
 *  <MsgEmpty type={3}/>
 * */
export default class MsgEmpty extends Component {
    constructor(props){
        super(props)
        this.state={
            typeData:{1:'@me', 2:'data', 3:'hi', 4:'send',5:'key',6:'tag',7:'task'},
            infoData:{
                1:'帮你聚合所有@你的消息，并且快速回\n复，不耽误任何时机',
                2:'群数据可以让你实时了解群内\n人员流动情况及发言情况',
                3:'欢迎语可以在有新用户入群时\n为你实时发布公告或入群须知',
                4:'一键群发图片、链接、小程序，还能追踪\n链接点击量，定时定群，轻松快捷',
                5:'关键词回复可以自动帮你在群内\n回复一些常见问题，省时省力',
                6:'设置主题后，小宠会按你的喜好\n推送文章哦~',
                7:''
            }
        }
    }

    handleClickGoTo=()=>{
        history.push('/grouppet/import')
    }

    render(){
        const {typeData,infoData} =this.state
        const {type} =this.props
        return <div className='empty-type-view'>
            <div className='sh-shareView'>
                <div className='shareView-type-img'>
                    <img src={`/images/newicon/pic_empty_${typeData[type]}.png`} alt="" />
                </div>
                {
                    infoData[type]!==''?
                        <div className='shareView-type-info'>
                            {
                                infoData[type].split('\n').map((item,index)=>{
                                    return <p key={index}>{item}</p>
                                })
                            }
                        </div>:null
                }
                <div className='shareView-type-btnBox' onTouchEnd={this.handleClickGoTo}>去导入</div>
            </div>
        </div>
    }

}

