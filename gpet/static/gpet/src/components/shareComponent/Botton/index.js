import React, {Component} from "react";
import ButtonLoading from '../ButtonLoading'
export default class Index extends Component {
    render() {
        const {isSave,text,loadText, loadColor,comfrimHandle} = this.props
        return (
            isSave? <div className='saveBtn' onClick={comfrimHandle}>{text}</div>
                :
                <div className='saveBtn' >
                    <ButtonLoading text={loadText} color={loadColor}/>
                </div>
        )
    }
}

/**
 *
 * <Botton isSave={isSave} text={'保存'} loadText={'保存中'} loadColor={'#fff'}
 comfrimHandle={this.handleSave}
 />
 * */
