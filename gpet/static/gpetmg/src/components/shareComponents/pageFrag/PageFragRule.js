import React, { Component } from 'react'
import './pageFrag.scss'
import {page_frag} from '../../../funStore/CommonPort'
export default class PageFragment extends Component {
    constructor(props){
        super(props)
        this.firstPage = this.firstPage.bind(this)
        this.lastPage = this.lastPage.bind(this)
        this.beforePage = this.beforePage.bind(this)
        this.nextPage = this.nextPage.bind(this)
        this.targetPage = this.targetPage.bind(this)
    }
    beforePage(e){
        e.stopPropagation()
        e.preventDefault()
        let url = this.props.url
        let paramas = this.props.searchParamas
        const _page = this.props.pageInfo.current_page-1
        const size = this.props.pageSize===undefined?'10':this.props.pageSize
        url = url + '?current_page='+_page+'&page_size='+size
        page_frag(url,paramas).then(res=>{
            this.props.pullData(res)
        })
    }
    nextPage(e){
        e.stopPropagation()
        e.preventDefault()
        let url = this.props.url
        let paramas = this.props.searchParamas
        const _page = this.props.pageInfo.current_page+1
        const size = this.props.pageSize===undefined?'10':this.props.pageSize
        url = url + '?current_page='+_page+'&page_size='+size
        page_frag(url,paramas).then(res=>{
            this.props.pullData(res)
        })
    }
    targetPage(e){
        e.stopPropagation()
        e.preventDefault()
        let url = this.props.url
        let paramas = this.props.searchParamas
        const _page = parseInt(e.target.id)
        const size = this.props.pageSize===undefined?'10':this.props.pageSize
        url = url + '?current_page='+_page+'&page_size='+size
        page_frag(url,paramas).then(res=>{
            this.props.pullData(res)
        })
    }
    lastPage(e){
        e.stopPropagation()
        e.preventDefault()
        let url = this.props.url
        let paramas = this.props.searchParamas
        let _page = this.props.pageInfo.total_page-1;
        const size = this.props.pageSize===undefined?'10':this.props.pageSize
        url = url + '?current_page='+_page+'&page_size='+size
        if(this.props.pageInfo.current_page!==this.props.pageInfo.total_page - 1){
            page_frag(url,paramas).then(res=>{
                this.props.pullData(res)
            })
        }
    }
    firstPage(e){
        e.stopPropagation()
        e.preventDefault()
        let url = this.props.url
        let paramas = this.props.searchParamas
        let _page = 0;
        const size = this.props.pageSize===undefined?'10':this.props.pageSize
        url = url + '?current_page='+_page+'&page_size='+size
        if(this.props.pageInfo.current_page!==0){
            page_frag(url,paramas).then(res=>{
                this.props.pullData(res)
            })
        }
    }
    render(){
        const {pageInfo} = this.props
        const totalPageNumber = pageInfo.total_page
        const current_pageNumber = pageInfo.current_page+1
        const items = []
        let start,end
        if(totalPageNumber<8){
            start = 1
            end = totalPageNumber
        }else if(current_pageNumber<5){
            start = 1
            end = 7
        }else if(current_pageNumber>totalPageNumber-4){
            start = totalPageNumber-6
            end = totalPageNumber
        }else {
            start = current_pageNumber-3
            end = current_pageNumber+3
        }
        for(var i = start; i <= end; i++){
            items.push(i)
        }
        return (
            <div className="pageFooter">
                <ul>
                    <li className="firstPage" onClick={this.firstPage}>首页</li>
                    <li className="prevPage" onClick={this.beforePage} style={{display:current_pageNumber===1?'none':'block'}}>上一页</li>
                    {
                        items.map((num)=>{
                            return <li
                                className={num===current_pageNumber?"pages currentPage":"pages"}
                                key={num}
                                id={num-1}
                                onClick={this.targetPage}
                            >{num}</li>
                        })
                    }
                    <li className="nextPage" onClick={this.nextPage} style={{display:current_pageNumber===totalPageNumber?'none':'block'}}>下一页</li>
                    <li className="lastPage" onClick={this.lastPage}>末页</li>
                </ul>
            </div>
        )
    }
}