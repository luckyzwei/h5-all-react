export const APP_ID = 'wx2f7c5155a1152486';//宝妈微社区

export const API_PATH = window.location.origin.includes('localhost') ? 'https://gdogdev.lizmom.cn'
    : window.location.origin.includes('gdogdev') ? 'https://gdogdev.lizmom.cn'
        : window.location.origin.includes('gdogprd') ? 'https://gdogprd.lizmom.cn'
            : 'https://gdogprd.gemii.cc'
