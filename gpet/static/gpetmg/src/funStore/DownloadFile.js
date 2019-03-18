const DownloadFile = (blobData, type, filename) => {
    var blob = new Blob([blobData], { type });
    var a = document.createElement("a");
    var href = window.URL.createObjectURL(blob);
    a.href = href; //创建下载的链接
    a.download = filename; //下载后文件名
    document.body.appendChild(a);
    a.click(); //点击下载
    document.body.removeChild(a); //下载完成移除元素
    window.URL.revokeObjectURL(href); //释放掉blob对象
};

export default DownloadFile;