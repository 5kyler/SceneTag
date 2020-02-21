function extract_inner_frames(video_pk,shot_pk,target_url) {
    $('img').click(function () {
        $.ajax({
            url: target_url,
            data: {
                'video_pk': video_pk,
                'shot_pk': shot_pk
            },
            success: function (data) {
                console.log(data)
                for (var i=0 ; i<data['new_shots'].length ; i++){
                    var img = $('<img id="#myImg"+i>');
                    img.attr('src', data['new_shots'][i]);
                    img.appendTo('.modal-body');
                }
            }
        })
    })
}



