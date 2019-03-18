import React from 'react';
import './modaldes.scss'
//收益明细modal
export const PorofitDescrip=({hideHandle})=>{
    return (
        <div className="modalWrapper">
            <div className="modalBox writeBox openAnt descripModal">
                <div className="modalTitle">
                    群收益说明
                </div>
                <div className='content'>
                    <p>1.拉群：拉群收益是指你的舒适度红包哦，舒适度红包分30天发放，如舒适度红包为30元，则每天1元，收益30天。</p>
                    <p>2.资讯点击：小宠在你拉的群内所发的链接被群友阅读时所产生的收益。</p>
                    <p>3.徒弟徒孙：作为师父师爷的你，可以躺赚徒弟徒孙的拉群和资讯点击收益，美滋滋。</p>
                    <p>4.领养费用：主人加一个新的小宠需要支付0.01的领养费哦。</p>
                    <p>5.其他：其他收益包含活动收益和一些其他的费用等等。</p>
                </div>
                <div className='btnBox'  onClick={hideHandle}>
                    <button className='confrimBtn'>知道啦！</button>
                </div>
                <div className='icon-cross closeBtn' onClick={hideHandle}/>
            </div>
        </div>
    )
}

//收益明细modal
export const TaskDescrip=({hideHandle})=>{
    return (
        <div className="modalWrapper">
            <div className="modalBox writeBox openAnt descripModal">
                <div className="modalTitle">
                    投放说明
                </div>
                <div className='content'>
                    <p>1.当小宠在主人的群内推荐内容时，每次群友阅读主人都会获得0.16元红包。阅读的人数越多，红包越多哦；</p>
                    <p>2.如果担心小宠发消息会打扰群友，主人可以在群列表页面中，选择对应的群关闭内容推荐；</p>
                    <p><img src="/images/newicon/taskDescrip.png" alt="" style={{width:'560px'}}/></p>
                    <p>3.在文章推送页面，主人可以看到过往3天我在群内发的内容。包含时间、内容样式以及投放的群。</p>
                </div>
                <div className='btnBox'  onClick={hideHandle}>
                    <button className='confrimBtn'>知道啦！</button>
                </div>
                <div className='icon-cross closeBtn' onClick={hideHandle}/>
            </div>
        </div>
    )
}

const Title = ({text})=>{
    return <div className='content-title'>
        <span className='title-line'/>
        <span>{text}</span>
        <span className='title-line'/>
    </div>
}
//徒弟徒孙规则modal
export const DiscipleRule=({hideHandle})=>{
    return (
        <div className="modalWrapper rewardRule">
            <div className="modalBox writeBox openAnt descripModal">
                <div className="content">
                    <Title text={'徒弟奖励'}/>
                    <p><span>1.</span><span>徒弟在导入群后，你会获得与徒弟收益等值的奖励，将分<span className="num">30</span>天发放到你的账户。(例：徒弟导入<span className="num">10</span>个群赚了<span className="num">300</span>元，你额外收益<span className="num">300</span>元)</span></p>
                    <p><span>2.</span><span>徒弟每获得一次点击收益，你也会获得<span className="num">0.02</span>元/点击的奖励。</span></p>
                    <Title text={'徒孙奖励'}/>
                    <p><span>1.</span><span>徒孙在导入群后，你会获得相当于徒孙收益一半的奖励，将分<span className="num">30</span>天发放到你的账户。（例:徒孙导入<span className="num">10</span>个群赚了<span className="num">300</span>元，你额外收益<span className="num">150</span>元）</span></p>
                    <p><span>2.</span><span>徒孙每获得一次点击收益，你也会获得<span className="num">0.02</span>元/点击的奖励。</span></p>
                </div>
                <div className='btnBox'  onClick={hideHandle}>
                    <button className='confrimBtn'>知道啦！</button>
                </div>
                <div className='icon-cross closeBtn' onClick={hideHandle}/>
            </div>
        </div>
    )
}


//元旦活动modal
export const NewYearsRules=({hideHandle})=>{
    return (
        <div className='profit-wrapper'>
            <div className="modalWrapper">
                <div className="modalBox writeBox openAnt descripModal">
                    <div className="modalTitle">
                        活动规则说明
                    </div>
                    <div className='content'>
                        <p>1.活动时间为1月1日至1月3日。在活动期间拉入的群，在后续得出舒适度为3个笑脸以上，即可获得红包，每群可获得6元，上不封顶。</p>
                        <p>2.聊天功能为活动限时体验，活动结束后关闭。</p>
                        <p>3.用户不得以任何恶意方式和行为参与本活动。一经发现，取消活动资格和奖励。</p>
                        <p>4.在法律许可范围内，本次活动的规则如有调整或变更以微小宠公众号“微小宠World”的发布为准。</p>
                    </div>
                    <div className='icon-cross closeBtn' onClick={hideHandle}/>
                </div>
            </div>
        </div>
    )
}