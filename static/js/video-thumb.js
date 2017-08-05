
function createThumbFromVideo(video){
    li = document.createElement("li")
    li.setAttribute("class", "thumb-container")

    li.setAttribute("link", "/play/" + video.id)
        img = document.createElement("img")
        img.src = "/static/thumb/" + video.id + ".png"
        img.setAttribute("data-image-error-source","/static/images/no-img.png")
        img.setAttribute("flip-template", "/static/flip/" + video.id + "-{index}.png")
        img.className += "thumb-image flip"
    li.append(img)
        lenSpan = document.createElement("span")
        lenSpan.setAttribute("class","length")
        lenSpan.innerHTML = durationStringFromSeconds(video.duration)
        li.append(lenSpan)

        titleSpan = document.createElement("span")
        titleSpan.setAttribute("class","title")
            titleSpan.innerHTML = video.title

        li.append(titleSpan)

    return li
}