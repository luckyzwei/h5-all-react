import {APP_ID} from '../constants/OriginName';
import {getCookie} from '../funStore/CommonFun'
import {getWechat} from '../funStore/CommonPort'
import {tongji} from '../constants/TrackEvent'
//eslint-disable-next-line
/* global location */
/* eslint no-restricted-globals: ["off", "location"] */
// eslint-disable-next-line
export const $wx = wx
const WXsharing = () => {
    let shareWord = {
        "title": '【领养小宠物】阅读就能返利',
        "desc": '注册即拿礼包，拼手速的时候到了~',
        "imgUrl": `https://gpetprd.gemii.cc/images/icon/share_logo.png`,
        "localHref": `${location.origin}/grouppet/adopt?sharing_user_id=`
    }
    /******************************微信分享操作*******************************/
    WXconfig()
    $wx.ready(function () {
        /*发送给朋友*/
        $wx.onMenuShareAppMessage({
            title: shareWord.title, // 分享标题
            desc: shareWord.desc, // 分享描述
            link: shareWord.localHref + getCookie('sharing_user_id'), // 分享链接
            imgUrl: shareWord.imgUrl, // 分享图标
            type: '', // 分享类型,music、video或link，不填默认为link
            dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
            success: function () {
                // 用户确认分享后执行的回调函数
                tongji('ShareAppMessage',location.href)
            },
            cancel: function () {
                // 用户取消分享后执行的回调函数
            }
        })

        /*分享到朋友圈*/
        $wx.onMenuShareTimeline({
            title: shareWord.title, // 分享标题
            link: shareWord.localHref + getCookie('sharing_user_id'), // 分享链接
            imgUrl: shareWord.imgUrl, // 分享图标
            success: function () {
                // 用户确认分享后执行的回调函数
                tongji('ShareTimeline',location.href)
            },
            cancel: function () {
                // 用户取消分享后执行的回调函数

            }
        })
    })
}

const WXconfig = () => {
    let currentUrl = location.href.split('#')[0];
    let url = encodeURIComponent(currentUrl);
    let configUrl=`?app_id=${APP_ID}&url=${url}`
    getWechat(configUrl).then(rea=>{
        if(rea.code === 1200){
            $wx.config({
                debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                appId: rea.data.app_id, // 必填，公众号的唯一标识
                timestamp: rea.data.timestamp, // 必填，生成签名的时间戳
                nonceStr: rea.data.noncestr, // 必填，生成签名的随机串
                signature: rea.data.signature,// 必填，签名，见附录1
                jsApiList: [
                    'onMenuShareAppMessage',
                    'onMenuShareTimeline',
                ] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
            })
        }
    })
}

export {WXsharing, WXconfig}
