function updatePageIndex(current,total,keyword,genUrl) {
    pages = document.getElementById("pages")

    pages.innerHTML = ""
    if(total > 1) {
        //Added previous page if necessary
        if( current != 0 ) {
          li = document.createElement("li")
              a = document.createElement("a")
              a.href = genUrl(keyword,current-1)
              a.setAttribute("aria-label", "Previous")
                span = document.createElement("span")
                span.setAttribute("aria-hidden","true")
                span.innerHTML = "«"
              a.append(span)
          li.append(a)

          pages.append(li)
        }

        for(var i=0; i<total; i++) {
            li = document.createElement("li")
            //li.id = "page-num"

            pgNum = i+1

            if(i == current) {
                li.setAttribute("class","active")
            }

            a = document.createElement("a")
            a.href = genUrl(keyword,i)
            a.innerHTML = pgNum

            li.append(a)

            pages.append(li)
        }

        if( (current+1) < total ) {
          li = document.createElement("li")
              a = document.createElement("a")
              a.href = genUrl(keyword,current-1)
              a.setAttribute("aria-label", "Next")
                span = document.createElement("span")
                span.setAttribute("aria-hidden","true")
                span.innerHTML = "»"
              a.append(span)
          li.append(a)

          pages.append(li)
        }
    }
}