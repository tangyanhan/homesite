
function createThumbFromVideo(video){
    li = document.createElement("li")
    li.setAttribute("class", "thumb")

    thumbContainer = document.createElement("div")
    thumbContainer.setAttribute("class","thumb-container")
        spanImg = document.createElement("span")
            spanImg.setAttribute("class", "thumb-image")
                a = document.createElement("a")
                a.setAttribute("class","item-link")
                a.href = "/play/" + video.id
                    img = document.createElement("img")
                    img.src = "/static/thumb/" + video.id + ".png"
                    img.setAttribute("data-image-error-source","{% static 'images/no-img.png' %}")
                a.append(img)
            spanImg.append(a)
    thumbContainer.append(spanImg)
        lenSpan = document.createElement("span")
        lenSpan.setAttribute("class","length")
        lenSpan.innerHTML = durationStringFromSeconds(video.duration)
        thumbContainer.append(lenSpan)

        titleSpan = document.createElement("span")
        titleSpan.setAttribute("class","title")
            titleLink = document.createElement("a")
            titleLink.setAttribute("class","title-item-link")
            titleLink.href = "/play/" + video.id
            titleLink.innerHTML = video.title

            titleSpan.append(titleLink)
        thumbContainer.append(titleSpan)

    li.append(thumbContainer)
    return li
}