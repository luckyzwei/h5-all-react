import React from 'react'
function createMarkup(text) {
    return {__html: text};
}
const desList = [
    {
        id: 1,
        star: [1],
        desWord: '如广告很多、没有人聊天的微信群。',
        desImg: 1
    },
    {
        id: 2,
        star: [1, 2],
        desWord: '如拼车群、内购群、互砍群等。',
        desImg: 2
    },
    {
        id: 3,
        star: [1, 2, 3],
        desWord: '如老乡群、好友群、亲友群、业主群等。',
        desImg: 3
    },
    {
        id: 4,
        star: [1, 2, 3, 4],
        desWord: '如宝妈群、球迷群、旅游群、宠物群等。',
        desImg: 4
    },
    {
        id: 5,
        star: [1, 2, 3, 4, 5],
        desWord: '舒适度3个笑脸以上且具有一定稀缺性、高质量的群。',
        desImg: 5
    }
]
const DesWord = ({text}) => {
    return <div className="desWord"  dangerouslySetInnerHTML={createMarkup(text)}/>
}

export const StarDescript = ({type,hide}) => {
    return <div className='modalWrapper' style={{overflow:'auto'}}>
        <div className='modalBox writeBox starModal'>
            {
                desList.map((item, index) => {
                    return item.id === type ?
                        <div key={index}>
                            <div className='starName'>
                                <span className='name'>舒适度:</span>
                                {
                                    item.star.map((v, i) => {
                                        return <span key={i} className='icon_star'/>
                                    })
                                }
                            </div>
                            <DesWord text={item.desWord}/>
                            {
                                item.desImg!==5? <div className='desImg'><img src={`/images/banner/star_des_${item.desImg}.png`} alt=''/> </div>:null
                            }
                        </div> : null
                })
            }
            <div className="icon-cross icon-circlecross" onClick={hide}/>
        </div>
    </div>

}