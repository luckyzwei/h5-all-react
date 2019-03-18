import {QQFACE_TEXT} from '../../constants/QQFaceMap'

const MsgTransform = (data, keywordList) => {
    const _reg = new RegExp('\\[(.+?)\\]', "g");
    const keywords = keywordList
    const matchArray = data.match(_reg);//筛选qqemojj表情
    let str = data
    str = str.replace(/\n\n\n/gi, '');
    str = str.replace(/↵/g, "<br>");//过滤换行标签
    str = str.replace(/_web/g, '');//过滤换行标签
    if (keywords.length !== 0) {
        for (var k = 0; k < keywords.length; k++) {
            str = str.replace(keywords[k].name, "<b style='color: #f36565'>" + keywords[k].name + "</b>")
        }
    }
    if (matchArray !== null) {
        var index;
        for (var i = 0; i < matchArray.length; i++) {
            if (QQFACE_TEXT.qqEmoji_array.indexOf(matchArray[i]) === -1 && QQFACE_TEXT.qqEmoji_array_chinese.indexOf(matchArray[i]) !== -1) {
                index = (QQFACE_TEXT.qqEmoji_array_chinese.indexOf(matchArray[i]));
            } else if (QQFACE_TEXT.qqEmoji_array_chinese.indexOf(matchArray[i]) === -1 && QQFACE_TEXT.qqEmoji_array.indexOf(matchArray[i]) !== -1) {
                index = (QQFACE_TEXT.qqEmoji_array.indexOf(matchArray[i]));
            }
            if (index === undefined) {
                str = str.replace(matchArray[i], '&nbsp;' + matchArray[i] + '&nbsp;');
            } else {
                str = str.replace(matchArray[i], '<img class = "qqemoji' + ' ' + "qqemoji" + index + '" name="' + index + '" src="/images/icon/spacer.png" alt=""/>');

            }
        }
    }

    return str
}

export default MsgTransform
