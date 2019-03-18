import React from 'react'
export const NoList=({type})=>{
    switch (type){
        case 'TASK_LIST':
            return <div className='new_noList'>小宠正在努力挑选优质文章中<br/>请耐心等待…</div>
        case 'GROUP_LIST':
            return <div className='new_noList'>主人还没有拉我入群哦～</div>
        case 'DISCIPLE_LIST':
            return <div className='new_noList'>主人还没有收到徒弟哦，<br/>点击下方按钮，马上收徒赚钱！</div>
        default:
            break;
    }
}