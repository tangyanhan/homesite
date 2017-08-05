function setupPlayerListener(rateUrl, recommendUrl, videoId) {
    $("video").height($("video").width() * (9/16));
    console.log("Width:" + $("video").width() + " Height:" + $("video").height())

    window.onresize = function() {
        $("video").height($("video").width() * (9/16));
    }

    loadRate(rateUrl, videoId, 0)
    loadRecommendVideos(recommendUrl, videoId)

    $("button.glyphicon.glyphicon-thumbs-up").click( function(){
        loadRate(rateUrl, videoId, 1)
    } )

    $("button.glyphicon.glyphicon-thumbs-down").click( function(){
        loadRate(rateUrl, videoId, -1)
    } )

    $("video, #play-button").click(function(){
        var video = $("video")[0]
        if( video.paused ) {
          video.play()
          $("#play-button").hide()
        }else{
          video.pause()
          $("#play-button").show()
        }
    })
}

function loadRate(url, videoId, option){
    $.post(url, { 'id':videoId, 'op':option,'csrfmiddlewaretoken': getCookie('csrftoken')},
        function(data,status){
        if(status == "success"){
            //var counts = JSON.parse(data)
            likeCount = data["like"]
            dislikeCount = data["dislike"]

            $("button.glyphicon.glyphicon-thumbs-up").text(likeCount)
            $("button.glyphicon.glyphicon-thumbs-down").text(dislikeCount)
        }
    })
}

function loadRecommendVideos(url, videoId){
  $.post(url, { 'id':videoId, 'csrfmiddlewaretoken': getCookie('csrftoken') },
    function(data,status){
      var vidList = $("#videos")
      vidList.empty()
      var videos = data['videos']
      for( var i=0; i<videos.length; i++ ) {
        video = videos[i]
        li = createThumbFromVideo(video)
        vidList.append(li)
      }
  })
}