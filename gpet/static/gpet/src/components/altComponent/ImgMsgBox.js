import React,{Component} from 'react'
import {LoadCartoonWhite} from '../shareComponent/LoadCartoon'

export default class ImgMsgBox extends Component {
    constructor(props){
        super(props)
        this.state = {
            maxNum: 5,
            loadingShow: true,
            imgShow: false,
            alertShow: false
        }
        this.loadErrorHandle = this.loadErrorHandle.bind(this)
        this.reLoadHandle = this.reLoadHandle.bind(this)
        this.loadSuccessHandle = this.loadSuccessHandle.bind(this)
    }
    loadErrorHandle (e,src) {
        let {maxNum} = this.state
        let imgObj = this.refs.imgObj
        if(maxNum > 0){
            this.setState({
                maxNum: --maxNum
            })
            setTimeout(function(){
                imgObj.src=src;
            },1000);
        }else{
            imgObj.style.height ='70px';
            imgObj.src='./images/icon/imgFail.png'
            this.setState({
                loadingShow: false,
                imgShow: true,
                alertShow: true
            })
        }
    }
    reLoadHandle (src) {
        this.setState({
            maxNum: 2,
            loadingShow: true,
            imgShow: false,
            alertShow: false
        })
        this.refs.imgObj.src=src
    }
    loadSuccessHandle (e) {
        if(e.target.src.substr(-11,11)==='imgFail.png'){
            this.setState({
                loadingShow: false,
                imgShow: true,
                alertShow: true
            })
        }else {
            this.refs.imgObj.style.maxHeight ='126px';
            this.setState({
                loadingShow: false,
                imgShow: true,
                alertShow: false
            })
        }
    }
    render () {
        let  {loadingShow,imgShow,alertShow} = this.state
        return (<div className='imgMsgBox'>
                    <div className="loadingBox" style={{display:loadingShow?'block':'none'}}>
                        <LoadCartoonWhite />
                    </div>
                    <img ref='imgObj' src = {this.props.src} alt='' 
                    onTouchEnd = {(e) => {this.props.showPreviewImg(e.target.src)}}
                    onError = {(e) => {this.loadErrorHandle(e,this.props.src)}}
                    onLoad = {(e)=>{this.loadSuccessHandle(e)}}
                    style={{display:imgShow?'block':'none'}}
                    />
                    <div className='alertBox' onTouchEnd={()=>{this.reLoadHandle(this.props.src)}} style={{display:alertShow?'block':'none'}}/>
                </div>)
    }
}
