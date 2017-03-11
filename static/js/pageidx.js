function updatePageIndex(current,total,keyword,genUrl) {
    pageIdx = document.getElementById("pageIdx")

    pageIdx.innerHTML=""

    if(total > 1) {
        if( current != 0 ) {
            li = document.createElement("li")
            a = document.createElement("a")
            a.href=genUrl(keyword,current-1)
            a.innerHTML = "< 上一页"

            li.append(a)

            pageIdx.append(li)
        }

        for(var i=0; i<total; i++) {
            li = document.createElement("li")
            li.id = "page-num"

            pgNum = i+1

            span = document.createElement("span")
            span.setAttribute("class","pc")
            span.innerHTML = pgNum

            if(i == current) {
                strong = document.createElement("strong")
                strong.append(span)
                li.append(strong)
                li.style.border = "0"
            }else{
                a = document.createElement("a")
                a.href = genUrl(keyword,i)
                a.append(span)
                li.append(a)
            }

            pageIdx.append(li)
        }

        if( current != (total-1) ) {
            li = document.createElement("li")
            a = document.createElement("a")
            a.href=genUrl(keyword,current-1)
            a.innerHTML = "< 下一页"

            li.append(a)

            pageIdx.append(li)
        }
    }

}