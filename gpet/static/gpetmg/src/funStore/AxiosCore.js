import Axios from 'axios'
import {API_PATH} from '../constants/OriginName'
import {getCookie} from '../funStore/CommonFun'
class AxiosCore {
    constructor() {
        this.options = {
            method: '',
            url: '',
            isAuth: true
        }
        // 存储请求队列
        this.queue = {}
    }

    // 销毁请求实例
    destroy(url) {
        delete this.queue[url]
        const queue = Object.keys(this.queue)
        return queue.length
    }

    // 请求拦截
    interceptors(instance, options) {
        // 添加请求拦截器
        instance.interceptors.request.use(config => {
            // 在发送请求之前做些什么
            return config
        }, error => {
            // 对请求错误做些什么
            return Promise.reject(error)
        })

        // 添加响应拦截器
        instance.interceptors.response.use((res) => {
            let {data} = res
            // 1.成功 返回的格式{code:200,data:{...},message:'...'}
            // if (data.code === 1200) {
            //     return data;
            // }
            //
            // // 2.unionId无效 重新登录/token过期
            // if (data.code === 1401||data.code === 1406) {
            //
            // }
            return data
        }, (error) => {
            // 4.系统错误，比如500、404等
            // if(error&&error.response){
            // }
            return Promise.reject({
                messageCode: 'sysError'
            })
        })
    }

    // 创建实例
    create(options) {
        let Author = options.isAuth ? {'Authorization': 'Bearer ' + getCookie('access_token_gpet')} : null
        let conf = {
            baseURL: API_PATH,
            headers: {
                'Content-Type': options.contentType,
                ...Author
            },
            // timeout: 2000,
            // withCredentials: false  // 是否携带cookie信息 默认false
        }
        return Axios.create(conf)
    }

    // 合并请求实例
    mergeReqest(instances = []) {
        //
    }

    // 请求实例
    request(options) {
        if (options.data) {
            let dataType = typeof options.data;
            let contentType = dataType === 'object' ? 'application/json;charset=UTF-8' : 'application/x-www-form-urlencoded'
            options.contentType = contentType
            options.data = dataType === 'object' ? JSON.stringify(options.data) : options.data
        }
        var instance = this.create(options)
        this.interceptors(instance, options)
        options = Object.assign({}, options)
        this.queue[options.url] = instance
        return instance(options)
    }

    requestFormData(options) {
        var instance = Axios.create({
            baseURL: API_PATH,
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            withCredentials: true
        })
        this.interceptors(instance, options.url)
        options = Object.assign({}, options)
        this.queue[options.url] = instance
        return instance(options)
    }
}

export default new AxiosCore()
/***
 * AxiosCore.request({url: API_URL.appStatus, method: 'get',data:parmas,isAuth:false})
 * url:请求接口
 * method：请求方法
 * data:传承
 * isAuth：是否是鉴权接口 true 是 false 否
 * */
