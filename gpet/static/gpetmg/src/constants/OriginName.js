export const API_PATH =  window.location.origin.includes('localhost') ? 'https://gpetprd.gemii.cc'
    : window.location.origin.includes('gpetdev') ? 'https://gpetdev.gemii.cc'
        : window.location.origin.includes('gpetprd') ? 'https://gpetprd.gemii.cc'
            : 'https://gpetprd.gemii.cc'


export const LOGIN_USER={
    username:'admin',
    password:'abcd1234'
}