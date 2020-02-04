function getClickedBtnPK(videoPK, framePK) {
    frameGrouping(videoPK,'/SceneTag/ajax/frames_grouping', framePK)
}
function frameGrouping(videoPK, url, framePK) {
    $.ajax({
        url : url,
        data : {
            name : 'frameGrouping',
            videoPK : videoPK,
            framePK : framePK,
            reload_url : '/SceneTag/frame/'+videoPK+'/page/1/',
        },
        success:function (data) {
            update_frames(data['reload_url']);
        },
        error:function (request,status,error) {
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
        }
    })
}