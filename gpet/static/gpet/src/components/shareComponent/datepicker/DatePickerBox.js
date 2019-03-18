import React, {Component} from 'react'
import DatePicker from './react-mobile-datepicker'
import './datepicker.scss'

export default class DatePickerBox extends Component {
    constructor(props) {
        super(props)
        this.state = {
            isOpen: true,
        }
    }

    componentDidMount() {
        let initTime = this.initTime()
        this.setState({
            time: initTime.time,
            min: initTime.min,
            max: initTime.max
        });
        document.querySelector('body').addEventListener('click',this.props.handleCancel);

    }

    initTime = () => {
        let {selectedTime} =this.props
        let current = selectedTime===''? new Date():new Date(selectedTime)
        let maxDay =new Date(new Date().getTime() + 2*24*3600*1000)
        let year = current.getFullYear()
        let month = current.getMonth() + 1
        let day = current.getDate()
        let hour = Math.ceil(current.getMinutes()/15)===4?current.getHours()+1:current.getHours()
        let minute = Math.ceil(current.getMinutes()/15)===4?0:Math.ceil(current.getMinutes()/15)*15
        // let hour = current.getHours()
        // let minute = current.getMinutes()
        return {
            time: new Date(`${year}/${month}/${day} ${hour}:${minute}`),
            min: new Date(`${year}/${month}/${day} 00:00`),
            max: new Date(`${maxDay.getFullYear()}/${maxDay.getMonth()+1}/${maxDay.getDate()} 23:59`)
        }
    }

    handleSelect = (time) => {
        this.setState({time})
        this.props.handleSelected(time,1)
    }

    render() {
        const {time, isOpen, min, max} = this.state;
        return (
            <div className="datepPickerBox">
                <DatePicker
                    theme={'ios'}
                    dateFormat={[['YYYY', (year) => {
                        return year + '年'
                    }], ['MM', (month) => {
                        return month + '月'
                    }], ['DD', (day) => {
                        return day + '日'
                    }], ['hh', (hour) => {
                        return hour + '时'
                    }], ['mm', (minute) => {
                        return minute + '分'
                    }]]}
                    showFormat={'YYYY/MM/DD hh:mm'}
                    dateSteps={[1, 1, 1, 1, 15]}
                    showHeader={false}
                    confirmText={'确认'}
                    cancelText={''}
                    value={time}
                    isOpen={isOpen}
                    min={min}
                    max={max}
                    onSelect={this.handleSelect}
                />
            </div>
        )
    }
}
