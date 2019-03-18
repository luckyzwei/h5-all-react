import React, {Component} from 'react'

export default class FirstLogin extends Component {
    constructor(props) {
        super(props)
        this.state = {
            step: 1
        }
        this.viewStep = this.viewStep.bind(this)
    }

    viewStep() {
        let self = this
        if (self.state.step === 4) return
        this.setState({
            step: ++self.state.step
        })
    }

    render() {
        const {step} = this.state
        const {hideFirstGide,marquee} = this.props
        return (
            <div className="modalWrapper firstLogin"
                 style={{position: 'absolute',paddingTop:marquee?'70px':0}} onClick={this.viewStep}>
                <div style={{height: '100%'}}>
                    <div className={`step step1`} style={{display: step === 1 ? 'block' : 'none'}}/>
                    <div className={`step step2`} style={{display: step === 2 ? 'block' : 'none'}}/>
                    <div className={`step step3`} style={{display: step === 3 ? 'block' : 'none'}}/>
                    <div className={`step step4`}/>
                    {step === 4 ? <div className="confirm-step" style={{display: step === 4 ? 'block' : 'none'}}
                                       onClick={hideFirstGide}>
                        <div className="confirmBtn">我知道啦</div>
                    </div> : null}
                </div>
            </div>
        )
    }
}
