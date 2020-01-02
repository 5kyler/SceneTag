from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from SceneTagSite import models
from SceneTagSite.utils import file_control

import cv2
import os
import json


# Create your views here.

def test(request):
    return render(request, 'SceneTagSite/test.html', {
    })


def video_list(request, list_page):
    videos = models.Video.objects.all().order_by('-pk')
    unregistered_file_count = len(file_control.get_unregistered_files())

    return render(request, 'SceneTagSite/video_list.html', {
        'videos': videos,
        'unreg_cnt': unregistered_file_count,
    })


def video_list_refresh(request):
    files = file_control.get_unregistered_files()

    for file in files:
        new_video = models.Video(programName=file)
        new_video.save()
        rel_path = file_control.move_file_to_pk_directory(file, new_video.pk)

        new_video.localFile.name = rel_path
        new_video.save()

        return HttpResponseRedirect(reverse('list', args='1'))


def video(request, video_id):
    video = models.Video.objects.get(pk=video_id)
    vid = cv2.VideoCapture(video.localFile.path)
    fps = vid.get(cv2.CAP_PROP_FPS)

    return render(request, 'SceneTagSite/video.html', {
        'video': video,
        'fps': fps,
    })


def edit_video(request, video_id):
    video = models.Video.objects.get(pk=video_id)

    frames = models.FrameList.objects.filter(video__pk=video_id).order_by('currentTimeStamp')

    return render(request, 'SceneTagSite/edit_video.html', {
        'video': video,
        'frames': frames,
    })


def extract_current_frame(request):
    response_datas = {
        'save_status': False,
    }
    video_pk = int(request.GET['video_pk'])

    video = models.Video.objects.get(pk=video_pk)
    video_path = video.localFile.path
    safe_path = video_path.encode('utf-8')
    vidcap = cv2.VideoCapture(str(safe_path))
    fps = vidcap.get(cv2.CAP_PROP_FPS)

    count = 0
    total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    total_frames = int(total_frames)

    return_list = []

    # 프레임 리프레쉬 추가

    success, image = vidcap.read()
    success = True
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
        success, image = vidcap.read()

        img_name = u'%05d.jpg' % count
        file_name = os.path.join(settings.MEDIA_ROOT, str(video_pk), img_name)
        save_status = cv2.imwrite(file_name, image)

        currentFrame = count

        frame = [currentFrame]
        return_list.append(frame)

        if save_status:
            response_datas['save_status'] = True
        count += 1
        if count >= (total_frames / fps):
            break

    for i in range(len(return_list)):
        for j in range(len(frame)):
            new_frame = models.FrameList(video=video, framerate=fps, currentFrame=return_list[i][j])
            new_frame.save()

    return return_list
