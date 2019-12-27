from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from SceneTagSite import models
from SceneTagSite.utils import file_control


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

    return render(request, 'SceneTagSite/video.html', {
        'video': video,
    })


def edit_video(request, video_id):
    video = models.Video.objects.get(pk=video_id)

    return render(request, 'SceneTagSite/edit_video.html', {
        'video': video,
    })