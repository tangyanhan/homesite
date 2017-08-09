// func(a, idx), to customize the <a> element inside pagination
function createPagination(parent, current, total, func){
    ul = document.createElement("ul");
    ul.classList.add("pagination");

    if(current>0) {
        li = document.createElement("li")
        li.classList.add("previous")
        a = document.createElement("a")
        a.innerHTML = "&larr; Prev"
        li.append(a)
        if( func ) {
            func(a, current-1)
        }
        ul.append(li)
    }

    for(var i=0; i<total; i++) {
        li = document.createElement("li")

        if(i == current) {
            li.classList.add("active")
        }
        a = document.createElement("a")
        a.innerHTML = i+1
        if( func ) {
            func(a, i);
        }
        li.append(a)
        ul.append(li)
    }

    if((current+1)<total) {
        li = document.createElement("li")
        li.classList.add("next")
        a = document.createElement("a")
        a.innerHTML = "&rarr; Next"
        li.append(a)
        if( func ) {
            func(a, current+1)
        }
        ul.append(li)
    }
    parent.append(ul);
}
