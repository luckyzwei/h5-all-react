import React from 'react'

export const CardTitle=({title})=>{
    return (
        <div className='cardTitle'>
            <span className='title-line'/>
            <span className='title-text'>{title}</span>
        </div>

    )
}