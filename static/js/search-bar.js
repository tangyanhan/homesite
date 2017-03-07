function getCookie(c_name)
{
    if (document.cookie.length>0)
    {
        c_start=document.cookie.indexOf(c_name + "=")
        if (c_start!=-1)
        {
            c_start=c_start + c_name.length+1
            c_end=document.cookie.indexOf(";",c_start)

            if (c_end==-1) c_end=document.cookie.length

            return unescape(document.cookie.substring(c_start,c_end))
        }
    }
    return ""
}

function setCookie(c_name,value,expiredays)
{
    var exdate=new Date()
    exdate.setDate(exdate.getDate()+expiredays)
    document.cookie=c_name+ "=" +escape(value)+
    ((expiredays==null) ? "" : "; expires="+exdate.toGMTString())
}

function checkCookie()
{
    username=getCookie('username')
    if (username!=null && username!="")
      {alert('Welcome again '+username+'!')}
    else
      {
      username=prompt('Please enter your name:',"")
      if (username!=null && username!="")
        {
        setCookie('username',username,365)
        }
      }
}

function getHistoryKeywords() {
    var historyKeywords = getCookie("history-keywords")
    if(historyKeywords.length > 0){
        keywords = historyKeywords.split("##")

        if(keywords.length == 0) {
            keywords = new Array(historyKeywords)
        }
        return keywords
    }
    return null
}

function addHistoryKeyword(keyword) {
    var historyKeywords = getHistoryKeywords()

    if(historyKeywords == null) {
        historyKeywords = new Array()
        historyKeywords.push(keyword)
    }else{
        if(historyKeywords[ historyKeywords.length - 1 ] != keyword) {
            historyKeywords.push(keyword) // add new keyword to font of the list
            for (var i = historyKeywords.length - 2; i >= 0; i--) {
                if( historyKeywords[i] == keyword ) {
                    historyKeywords.splice(i,1)
                }
            }
        }
    }

    cookieStr = historyKeywords.join("##")

    setCookie("history-keywords",cookieStr,30)
}

