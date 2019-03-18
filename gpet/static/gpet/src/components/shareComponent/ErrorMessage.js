import React from 'react'
/**
 * type
 * 1:pic_empty_@me @我
 * 2:pic_empty_data 群数据
 * 3:pic_empty_hi 入群欢迎语
 * 4:pic_empty_send 群发消息
 * 5:创建群发
 * */
const infoData={
    1:'群里暂时还没有人@你哦\n',
    2:'暂时没有群数据\n',
    3:'欢迎语可以在有新用户入群时\n为你实时发布公告或入群须知',
    4:'你暂时还没有群发任务哦\n可以给小宠私聊发个数字 7 试试呢',
    5:'你上传的图片、链接、小程序已失效(10分钟)\n如需群发可再次给小宠私聊发个数字 7',//创建群发没有素材显示error
}
export const ErrorNoNews=({type})=>{
    return (
        <div className='new-containter'>
            <div className='sh-shareView'>
                <div className='shareView-info'>
                    <p>{infoData[type].split('\n')[0]}</p>
                    <p>{infoData[type].split('\n')[1]}</p>
                </div>
                <div className='shareView-img'>
                    <img src={'/images/icon/pic_kongzhuangtai.png'} alt="" />
                </div>
            </div>
        </div>

    )
}