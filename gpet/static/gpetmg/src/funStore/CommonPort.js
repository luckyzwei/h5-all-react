import {API_PATH} from '../constants/OriginName'
import {API_URL} from '../constants/Api'
import AxiosCore from './AxiosCore'
import Axios from "axios/index";
import DownloadFile from "./DownloadFile";

/** 分页 */
export const page_frag=(url,params)=>{
    return AxiosCore.request({url: url , method: 'POST',data:params, isAuth:false})
}
/** 获取token */
export const login_get_token=(parmas)=>{
    return AxiosCore.request({url: API_URL.auth, method: 'POST', data: parmas, isAuth:false})
}

/** 提现列表 */
export const review_list=(urlComple,params)=>{
    return AxiosCore.request({url: API_URL.reviewList+urlComple, method: 'POST',data:params, isAuth:false})
}
export const review=(params)=>{
    return AxiosCore.request({url: API_URL.review, method: 'POST',data:params, isAuth:false})
}

/** 问题反馈 */
export const problem_list=(urlComple,params)=>{
    return AxiosCore.request({url: API_URL.problemList+urlComple, method: 'POST',data:params ,isAuth:false})
}
export const problem_export=(params)=>{
    return AxiosCore.request({url: API_URL.problemExport, method: 'POST',data:params,isAuth:false})
}
export const problems=(url,params)=>{
    return AxiosCore.request({url: API_URL.problems, method: 'GET', isAuth:false})
}

/** 问题反馈 */
export const export_excel=(url,params,filename)=>{
    return Axios({
        url:API_PATH+url,
        method:"POST",
        headers:{'Content-type':'application/vnd.ms-excel;chartset=utf-8'},
        data:params,
        responseType: 'blob'
    }).then(function(res){
        DownloadFile(res.data, "application/vnd.ms-excel", filename);
    }).catch(function(error){
        console.log('下载失败')
    });
}





















