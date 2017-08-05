function setupThumbListener() {
    resizeThumb()

    $(window).resize( function(){
        resizeThumb()
    } );

    $(".thumb-container").click(function(){
        window.open($(this).attr("link"));
    });
}

function resizeThumb() {
    var thumbWidth = $(".thumb-container").width()
    var thumbHeight = thumbWidth * 9 / 16
    $(".thumb-container").css("height", thumbHeight)
    // Scale image manually
    $(".thumb-image").css("width", thumbWidth)
    $(".thumb-image").css("height", thumbHeight)
}

function durationStringFromSeconds(seconds) {
	var duration = ""

	var sec = seconds % 60
	var min = parseInt(seconds / 60)
	var hour = 0
	if (min >= 60) {
		hour = parseInt(min / 60)
		min %= 60

		duration += hour
	 }

	duration = duration + ((hour>0)? ":" : "") +((min<10)? "0" : "") + min + ":" + ((sec<10)? "0" :"") + sec

	return duration
}

function createThumbFromVideo(video) {
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