export const APP_ID = 'wx6f2f31d8d2b80e54' //新公众号 微小宠

export const API_PATH =  window.location.origin.includes('localhost') ? 'https://gpetdev.gemii.cc'
        : window.location.origin.includes('gpetdev') ? 'https://gpetdev.gemii.cc'
            : window.location.origin.includes('gpetprd') ? 'https://gpetprd.gemii.cc'
                : 'https://gpetprd.gemii.cc'
