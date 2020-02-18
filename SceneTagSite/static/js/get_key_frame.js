function getCurrentVideoFrame(video_pk,target_url,fps) {
    try {
        var fixed_fps = parseFloat(fps).toFixed(2)
        var frameRate = fixed_fps
        var myPlayer = videojs('video_id');
        myPlayer.ready(function () {
            // myPlayer.currentTime(120);
            var whereYouAt = myPlayer.currentTime();
            var theCurrentFrame = Math.floor(whereYouAt * frameRate);

            var currentTimeStamp = whereYouAt
            currentTimeStamp = parseFloat(currentTimeStamp).toFixed(2) // 소수 셋째 자리에서 반올림
            var currentFrame = theCurrentFrame
            $.ajax({
                    url: target_url,
                    data: {
                        'video_pk' : video_pk,
                        'currentTimeStamp': currentTimeStamp,
                        'currentFrame': currentFrame,
                    },
                    success: function (data) {
                        $('#popUP').modal('show');
                        setTimeout(function() {
                            $('#popUP').modal('hide');
                        }, 500);
                    }
                })
            });
        }
    catch(e) {
        console.log("FAIL!!!!!!!!!!!!!!!")
    }
}