function updatePageIndex(current,total,keyword,genUrl) {
    pages = document.getElementById("pages")

    pages.innerHTML = ""
    if(total > 1) {
        //Added previous page if necessary
        if( current != 0 ) {
            prev = document.createElement("span")
            prev.setAttribute("class","next-page")
                subPrev = document.createElement("span")
                subPrev.setAttribute("class","previous")
                    a = document.createElement("a")
                    a.href = genUrl(keyword,current-1)
                    a.innerHTML = "<i class=\"fa fa-chevron-left\"></i>"
                    subPrev.append(a)
                prev.append(subPrev)
            pages.append(prev)
        }

        numSpan = document.createElement("span")
        numSpan.setAttribute("class","pages no-border-radius-right")

        for(var i=0; i<total; i++) {
            li = document.createElement("li")
            li.id = "page-num"

            pgNum = i+1

            span = document.createElement("span")
            span.setAttribute("class","page")
                a = document.createElement("a")
                a.innerHTML = pgNum
                a.href = genUrl(keyword,i)
                if( i == current) {
                    a.setAttribute("class","current")
                }
                span.append(a)
            numSpan.append(span)
        }
        pages.append(numSpan)
    }
}