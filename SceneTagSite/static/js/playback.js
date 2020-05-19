var durationTime = document.getElementById("video_id");
durationTime.addEventListener('loadedmetadata', function () {
    // console.log(durationTime.duration);
})

function timecode2sec(timecode) {
    time_split = timecode.split(":");
    hours = parseInt(time_split[0]);
    minutes = parseInt(time_split[1]);
    seconds = parseFloat(time_split[2]);
    time_sec = 3600 * hours + 60 * minutes + seconds;

    return time_sec
}

function playback(startTime, endTime) {
    start_sec = timecode2sec(startTime);
    end_sec = timecode2sec(endTime);
    console.log("start: %s(%d), end: %s(%d)", startTime, start_sec, endTime, end_sec,);

    try {
        var myPlayer = videojs('video_id');
        myPlayer.ready(function () {
            myPlayer.currentTime(start_sec);
            this.on('timeupdate', function () {
                var whereYouAt = myPlayer.currentTime();

                if(this.currentTime() >= end_sec) {
                    myPlayer.pause();
                }
            })
        });
        myPlayer.play();
    }
    catch(e) {
        console.log("FAIL!!!!!!!!!!!!!!!")
    }
}

