import React from 'react'
import FeaturesRow from './FeaturesRow'
const featuresData = {
    features1:[
        {imgSrc:'-28px -58px', text:'拉群', goLink:'/grouppet/import',event:'home_import'},
        { imgSrc:'-102px -58px', text:'收徒', goLink:'/grouppet/share',event:'home_share'},
        { imgSrc:'-176px -58px', text:'文章推送', goLink:'/grouppet/tasknote',event:'home_tasknote'},
        { imgSrc:'-250px -58px', text:'群收益', goLink:'/grouppet/profit',event:'home_profit'}

    ],
    features2:[
        {imgSrc:'-28px -132px', text:'群数据', goLink:'/grouppet/data',event:'home_data'},
        { imgSrc:'-102px -132px', text:'欢迎语', goLink:'/grouppet/createwelcome',event:'home_welcome'},
        { imgSrc:'-176px -132px', text:'群发消息', goLink:'/grouppet/messmsg',event:'home_messmsg'},
        { imgSrc:'-250px -132px', text:'关键词回复', goLink:'/grouppet/keyword/keywordlist',event:'home_keyword'}

    ],
    features3:[
        {imgSrc:'-324px -132px', text:'有人@我', goLink:'/grouppet/altme',event:'import_@wo'},
        {imgSrc:'-398px -132px', text:'敬请期待', goLink:''}
    ]
}
export const SkillCard =({history})=>{
    return <div className='exclusiveCardBox'>
        <div className='skillCardBox'>
            <FeaturesRow featuresData={featuresData.features1} history={history}/>
        </div>
    </div>
}


export const ExclusiveCard=({history})=>{
    return <div className='exclusiveCardBox'>
        <FeaturesRow featuresData={featuresData.features2} history={history}/>
        <FeaturesRow featuresData={featuresData.features3} history={history}/>
    </div>


}


