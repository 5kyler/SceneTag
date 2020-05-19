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

function timeFormat(sectime) {
    var sec_time = parseFloat(sectime).toFixed();
    hours = parseInt(sec_time/3600);
    minutes = parseInt((sec_time%3600)/60);
    seconds = sec_time%60;

    if (hours.toString().length===1) hours = "0" + hours;
    if (minutes.toString().length===1) minutes = "0" + minutes;
    if (seconds.toString().length===1) seconds = "0" + seconds;

    time_sec = hours + ":" + minutes + ":" + seconds;

    return time_sec

}

function playback(startTime, endTime) {
    //start_sec = timecode2sec(startTime);
    //end_sec = timecode2sec(endTime);
    //console.log("start: %s(%d), end: %s(%d)", startTime, start_sec, endTime, end_sec,);

    try {
        var myPlayer = videojs('video_id');
        myPlayer.ready(function () {
            myPlayer.currentTime(startTime);
            this.on('timeupdate', function () {
                var whereYouAt = myPlayer.currentTime();

                if(this.currentTime() >= endTime) {
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

