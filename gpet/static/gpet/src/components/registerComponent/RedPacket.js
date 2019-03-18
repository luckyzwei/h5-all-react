import React, {Component} from 'react'
import Protocal from './Protocal'
import {tongji} from "../../constants/TrackEvent";
import {receive_red_packet} from "../../funStore/CommonPort";
import {$wx} from '../../funStore/WXsharing'
import './index.scss'

export default class RedPacket extends Component {
    constructor(props) {
        super(props)
        this.state = {
            checkProtocal: true,
            redPacketStatus: 'NOT_OPEN',//0:未开启 1:开启
            isReady: false,
            money: '0:00'
        }
    }

    handleClickRadio = () => {
        this.setState({
            checkProtocal: !this.state.checkProtocal,
        })
    }

    openRedPacket = () => {
        //获取红包接口
        receive_red_packet().then(resData => {
            if (resData.code === 1200)
                this.setState({
                    money: resData.data.red_packet,
                    redPacketStatus: 'OPEN'
                })
            localStorage.setItem("firstFlag", true)
        })
        tongji('first_redEnvelope')
    }

    goToImportGroup = () => {
        // eslint-disable-next-line
        $wx.closeWindow()
    }

    render() {
        const {money, redPacketStatus, checkProtocal, isReady} = this.state
        const {hideRedModel} = this.props
        return (
            <div className='modalWrapper'>
                {
                    redPacketStatus === 'OPEN'
                        ?
                        <div className="modalBox registerSuccess">
                            <div className='open_red'>
                                <div className="money">
                                    ¥ <span>{money}</span>
                                </div>
                                <div className='goBtn' onClick={this.goToImportGroup}>
                                    继续领红包
                                </div>
                            </div>
                            <div className='icon-cross closeBtn' onClick={hideRedModel}/>
                        </div>
                        :
                        isReady ? <Protocal hide={() => {
                                this.setState({isReady: false})
                            }}/>
                            : <div className="modalBox registerSuccess">
                                <div className='red_bg'>
                                    <img className='redStatus'
                                         src={`/images/newicon/${checkProtocal ? 'red_open' : 'red_close'}.png`} alt=""
                                         onClick={checkProtocal ? this.openRedPacket : null}
                                    />
                                    <div className="protocal">
                                        <span className={checkProtocal ? "checkBox checked" : "checkBox"}
                                              onClick={this.handleClickRadio}
                                        />
                                        我已同意
                                        <span style={{textDecoration: 'underline'}}
                                              onClick={() => {
                                                  this.setState({isReady: true});
                                                  tongji('first_redEnvelope_protocol');
                                              }}
                                        >《微小宠领养协议》</span>
                                    </div>
                                </div>
                            </div>
                }
            </div>

        )
    }
}
