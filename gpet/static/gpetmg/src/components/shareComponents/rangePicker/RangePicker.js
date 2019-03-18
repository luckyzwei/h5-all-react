import React,{Component} from 'react'
import DatePicker from 'antd/lib/date-picker';
import 'antd/lib/date-picker/style/css'; 
import locale from 'antd/lib/date-picker/locale/zh_CN';
import "./rangePicker.scss"

export default class RangePicker extends Component {
    constructor(props){
        super(props)
        this.state= {
            
        }
    }
    onChange = (date, dateString) => {
        if(this.props.setDateParams){
            this.props.setDateParams(dateString,this.props.paramaName)
        }
    }
    onOpenChange = (status) => {
        // console.log(status,2) //true or false
    }

    render(){
        const {disabledDate,disabled,label} = this.props
        return (
            <div className='datePicker'>
                {label? <div className='datePickerLabel'>{label}</div>:null}
                <DatePicker.RangePicker
                    defaultValue={this.props.defaultValue}
                    locale={locale}
                    className={"dateSelect"}
                    dropdownClassName={"dateRangePicker"}
                    getCalendarContainer={()=>document.getElementsByClassName('dateSelect')[0]}
                    onOpenChange={this.onOpenChange}
                    showTime={false}
                    allowClear = {true}
                    onChange={this.onChange}
                    disabledDate={disabledDate}
                    disabled={disabled}
                />
            </div>

           
        )
    }
}