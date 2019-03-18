import React, {Component} from 'react'
import {tongji} from '../../../constants/TrackEvent'
import './swiper-3.4.2.min.css'
import './swipe.scss'
export default class Banner extends Component {
    componentDidMount() {
        const self = this
        // eslint-disable-next-line
        var $Swiper = Swiper
        new $Swiper('#banner-swiper', {
            direction: 'horizontal',
            loop: true, //是否轮播 true 是 false 否
            autoplay: 5000,
            autoplayDisableOnInteraction: false,
            // 如果需要分页器
            pagination: '#banner-swiper-pagination',
            paginationType: 'bullets',
            onClick: function (swiper) {
                if (swiper.realIndex === '0') {
                    self.handleGoOne()
                }
                else if (swiper.realIndex === '1') {
                    self.handleGoTwo()
                }
                else{
                    self.handleGoThree()
                }
            }
        })
    }

    handleGoOne=()=>{
        window.location.href = 'http://mp.weixin.qq.com/s?__biz=MzU1OTU5OTIxNw==&mid=2247483743&idx=1&sn=a8fa4946b1c3e4242695b28a7d530b09&chksm=fc159a41cb62135744f666bce9a85381f8d56bcee445db0680d055aaa2f23635b0bb467b95ff#rd'
        tongji('home_weixinPublic')
    }
    handleGoTwo=()=>{
        this.props.history.push('/grouppet/star')
        tongji('home_shuShiDu')
    }

    handleGoThree = () => {
        // this.props.history.push('/grouppet/newyears')
        // tongji('home_yuanDan')
    }

    render() {
        return (
            <div className="swiper-container" id='banner-swiper'>
                <div className="swiper-wrapper">
                    {/*元旦活动*/}
                    {/*<div className="swiper-slide banner banner_1"/>*/}
                    {/*公众号推文*/}
                    <div className="swiper-slide banner banner_2">
                        <span className='bannerButton'/>
                    </div>
                    {/*赚钱攻略*/}
                    <div className="swiper-slide banner banner_3"/>
                </div>
                <div className="swiper-pagination" id="banner-swiper-pagination"/>
            </div>
        )
    }
}
