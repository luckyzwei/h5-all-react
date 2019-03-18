import React, {Component} from "react";

export default class ButtonLoading extends Component {
    render() {
        const {text, color} = this.props
        return (
            <div className='loadingBox-butt' style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                <div className='desc' style={{marginRight: 20}}>{text}</div>
                <div className="loader loader--style7" title="6">
                    <svg version="1.1" id="Layer_1" x="0px" y="0px" width="30px" height="16px">
                        <circle cx="4" cy="4" r="3" fill={color}>
                            <animate attributeName="opacity" attributeType="XML"
                                     values="1; .2; 1"
                                     begin="0s" dur="0.6s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="14" cy="4" r="3" fill={color}>
                            <animate attributeName="opacity" attributeType="XML"
                                     values="1; .2; 1"
                                     begin="0.2s" dur="0.6s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="24" cy="4" r="3" fill={color}>
                            <animate attributeName="opacity" attributeType="XML"
                                     values="1; .2; 1"
                                     begin="0.4s" dur="0.6s" repeatCount="indefinite"/>
                        </circle>
                    </svg>
                </div>
            </div>
        )
    }
}
