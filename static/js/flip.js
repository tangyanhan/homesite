var timer
var originalSrc
function getAttr(element, attr, defValue) {
    var value = element.attr(attr)
    if( !value ) {
        return defValue
    }
    return value
}

function startFlip(element, template, interval, next, start, end) {
    if(next > end) {
        next = start
    }
    var imgSrc = template.replace(/{index}/, next + "")
    element.attr("src", imgSrc)
    timer = setTimeout(startFlip.bind(null, element, template, interval, next+1, start, end), interval)
}

function stopFlip(element, imgSrc) {
    clearTimeout(timer)
    element.attr("src", imgSrc)
}

function setupFlipListener() {
    $("img.flip").mouseover(function(){
        var flipTemplate = $(this).attr("flip-template");
        if( flipTemplate ) {
            console.log(flipTemplate);
        }
        var flipInterval = getAttr($(this), "flip-interval", 800)
        var flipStart = getAttr($(this), "flip-start", 1)
        var flipEnd = getAttr($(this), "flip-end", 16)
        originalSrc = $(this).attr("src")
        timer = setTimeout(startFlip.bind(null, $(this), flipTemplate, flipInterval, flipStart, flipStart, flipEnd), 1000)
    });

    $("img.flip").mouseleave(function(){
        stopFlip($(this), originalSrc)
    });

}