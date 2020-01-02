function getCurrentVideoFrame(video_pk,target_url) {
    try {
        var myPlayer = videojs('video_id')
        myPlayer.ready(function () {

            $.ajax({
                    url: target_url,
                    data: {
                        'video_pk' : video_pk,
                    },
                    success: function (data) {
                    }
                })
            });
        }
    catch(e) {
        console.log("fail")
    }
}