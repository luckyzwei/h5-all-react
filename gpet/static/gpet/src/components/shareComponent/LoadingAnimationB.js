import React, {Component} from 'react'

export default class LoadingAnimationB extends Component {
    render() {
        return (
            <div className="loadAnimationB">
                <div className="loadBox" style={{width: '80px', height: '80px', margin: '0 auto'}}>
                    <svg className="lds-message" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"
                         viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                        <g transform="translate(25 50)">
                            <circle cx="0" cy="0" r="6" fill="#0a7be5" transform="scale(0.985026 0.985026)">
                                <animateTransform attributeName="transform" type="scale" begin="-0.3333333333333333s"
                                                  calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0"
                                                  keyTimes="0;0.5;1" dur="1s"
                                                  repeatCount="indefinite"></animateTransform>
                            </circle>
                        </g>
                        <g transform="translate(50 50)">
                            <circle cx="0" cy="0" r="6" fill="#50bdf9" transform="scale(0.648 0.648)">
                                <animateTransform attributeName="transform" type="scale" begin="-0.16666666666666666s"
                                                  calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0"
                                                  keyTimes="0;0.5;1" dur="1s"
                                                  repeatCount="indefinite"></animateTransform>
                            </circle>
                        </g>
                        <g transform="translate(75 50)">
                            <circle cx="0" cy="0" r="6" fill="#38abae" transform="scale(0.186044 0.186044)">
                                <animateTransform attributeName="transform" type="scale" begin="0s" calcMode="spline"
                                                  keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0" keyTimes="0;0.5;1"
                                                  dur="1s" repeatCount="indefinite"></animateTransform>
                            </circle>
                        </g>
                    </svg>
                </div>
            </div>
        )
    }
}