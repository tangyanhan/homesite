var suggestUrl = "/suggest/"

function setupSearchBarListener(sugUrl) {
    suggestUrl = sugUrl

    $("#sug-list").hide()
    $("#search_button").click(function(){
      search( $("#keyword_input").val() )
    })

    $("#keyword_input").focus(function(){
        showSuggestion()
    })

    $("#keyword_input").keyup(function(event){
        showSuggestion()
    })

    $("#keyword_input").focus(function(){
        showSuggestion()
    })

    $(document).click(function(e){
     e = window.event || e; // 兼容IE7
     obj = $(e.srcElement || e.target);
        if ($(obj).is("#sug-list,#sug-list *,#keyword_input")) {
       } else {
        $("#sug-list").hide()
     }
    });

    $('#keyword_input').bind('keypress',function(event){
        if(event.keyCode == "13")
        {
            search($(this).val())
        }
    })
}

function showSuggestionList(keywords) {
    if(keywords.length == 0) return

    var ul = $("#sug-list")
    ul.empty()
    for (var i = keywords.length - 1; i >= 0; i--) {
        li = document.createElement("li")
            a = document.createElement("a")
            keyword = keywords[i][0]
            count = keywords[i][1]
            a.href = getKeywordUrl(keyword,0)

            a.innerHTML = keyword + "   <span class=\"pull-right\">" + count + (count>1?" results":" result") + "</span>"
            li.append(a)
        ul.append(li)
    }
    $("#sug-list").show()
}

function showSuggestion() {
    var keyword = document.getElementById("keyword_input").value

    keyword = processKeyword(keyword)

    if(keyword.length == 0) {
        var historyKeywords = getCookie("history-keywords")
        if(historyKeywords.length > 0){
            keywords = historyKeywords.split("##")

            showSuggestionList(keywords)
        }
    }else{
		$.post(suggestUrl, { 'keyword':keyword, 'csrfmiddlewaretoken': getCookie('csrftoken')},
			function(data,status){
			if(status == "success"){
				var keywords = data['keywords']
				showSuggestionList(keywords)
			}
		})
    }

}

function search(keyword) {

    if(typeof keyword == "undefined" || keyword==null){
        keyword = $("#keyword_input").val()
    }

	keyword = processKeyword(keyword)

    if(keyword.length == 0 || keyword == " ") return false

    //Add it to cookie if it does not exist
    addHistoryKeyword(keyword)

    $("#keyword_input").blur()
    $("#sug-list").hide()

	window.location.href = getKeywordUrl(keyword, 0)
}

function processKeyword(keyword){
	keyword = keyword.toLowerCase()
    keyword = keyword.replace(/\s+/, ' ')
    keyword = keyword.replace(/&/,'')

    return keyword
}

function getKeywordUrl(keyword, pageIndex) {
	return "/search/?&keyword=" + keyword + "&idx=" + pageIndex
}

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

function loadSearchPage(keyword, pageIndex, pageNum, results) {
	$("#search_query_query").value = keyword

	// Deal with title
	title = "Videos"
	if( keyword.length > 0 ) {
		title = keyword
		if( pageIndex > 0 ) {
			title = title + "#" + pageIndex
		}
	}

	document.title = title

	var videoDiv = $("#videos")
	videoDiv.empty() //remove old results

    var emptyHint = document.getElementById("empty-hint")
	if( results.length == 0 ) {
	    emptyHint.visible = true
	    if(keyword.length == 0) {
	        emptyHint.innerHTML = "No videos imported yet"
	    }else{
	        emptyHint.innerHTML = "No results found relating to <b>" + keyword + "</b>"
	    }
	}else{
	    emptyHint.visible = false;
	}

    for(var i=0; i<results.length; i++) {
        video = results[i]
        li = createThumbFromVideo(video)
        videoDiv.append(li)
    }
}

