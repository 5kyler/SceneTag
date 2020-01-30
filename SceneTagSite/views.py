from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from SceneTagSite import models
from SceneTagSite.utils import file_control
from SceneTagSite.utils import frame_extractor

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View

import cv2
import os
import json


# Create your views here.


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


def shot_list(request, video_id):
    video = models.Video.objects.get(pk=video_id)
    vid = cv2.VideoCapture(video.localFile.path)
    fps = vid.get(cv2.CAP_PROP_FPS)

    return render(request, 'SceneTagSite/shot_list.html', {
        'video': video,
        'fps': fps,
    })


class FrameBrowse(View):
    def __init__(self):
        return

    def get(self, request, video_id, page_num=1):
        if request.is_ajax():
            return self.update_frames(request, video_id, page_num)
        else:
            return self.get_normal(request, video_id, page_num)

    def get_normal(self, request, video_id, page_num):
        video = models.Video.objects.get(pk=video_id)

        return render(request, 'SceneTagSite/frame_list.html',
                      {
                          'video': video,
                      })

    def update_frames(self, request, video_id, page_num):
        video = models.Video.objects.get(pk=video_id)
        frame_list = models.FrameList.objects.filter(video=video, shot__isnull=True).order_by('currentFrame')

        paginator = Paginator(frame_list, 10)
        cur_framepage = page_num
        frames = paginator.page(page_num)
        max_framepage = paginator.num_pages

        return render(request, 'SceneTagSite/update_frame.html',
                      {'video': video,
                       'frames': frames,
                       'cur_framepage': cur_framepage,
                       'max_framepage': max_framepage,
                       })


def extract_current_frame(request, video_id):
    video = models.Video.objects.get(pk=video_id)
    video_path = video.localFile.path
    vid = cv2.VideoCapture(video_path)
    fps = vid.get(cv2.CAP_PROP_FPS)

    count = 0
    total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    return_list = []

    success = True
    while success:
        vid.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))
        success, img = vid.read()

        current_frame = int(count * fps)

        if current_frame > total_frames:
            break
        return_list.append(current_frame)

        if count >= total_frames:
            break

        count += 1

    for i in range(len(return_list)):
        new_frame = models.FrameList(video=video, framerate=fps, currentFrame=return_list[i])
        new_frame.save()

    return HttpResponseRedirect(reverse('frame_list', args=video_id))


def ajax_get_frame_url(request):
    response_datas = []

    if request.GET['name'] == 'getFrameURL':
        response_data = {}
        videoNum = int(request.GET['VideoNum'])
        frameNum = int(request.GET['frameNum'])
        video = models.Video.objects.get(pk=videoNum)
        response_data['tagID'] = request.GET['tagID']
        response_data['URL'] = frame_extractor.get_frame_url(videoNum, video.localFile.path, frameNum)


