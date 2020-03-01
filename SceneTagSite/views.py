from __future__ import unicode_literals

import csv

from django.core import serializers
from django.db.models import Sum
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from SceneTagSite import models
from SceneTagSite.utils import file_control
from SceneTagSite.utils import frame_extractor
from collections import Counter

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View

import cv2
import os
import json
import re

from .forms import ShotRotationForm, ObjectTagForm, ObjectTaggingForm, ResultTagForm
from .models import ShotRotation, ObjectTag, ManualTagResult, AutoObjectTag

from datetime import datetime, date
import time


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


class ShotBrowse(View):
    def __init__(self):
        return

    def get(self, request, video_id, page_num=1):
        if request.is_ajax():
            return self.update_shot(request, video_id, page_num)
        else:
            return self.get_normal(request, video_id, page_num)

    def get_normal(self, request, video_id, page_num):
        video = models.Video.objects.get(pk=video_id)

        return render(request, 'SceneTagSite/shot_list.html',
                      {
                          'video': video,
                      })

    def update_shot(self, request, video_id, page_num):
        video = models.Video.objects.get(pk=video_id)
        vid = cv2.VideoCapture(video.localFile.path)
        fps = vid.get(cv2.CAP_PROP_FPS)
        shot_list = models.Shot.objects.filter(video=video)
        paginator = Paginator(shot_list, 10)
        cur_shotpage = page_num
        shots = paginator.page(page_num)
        max_shotpage = paginator.num_pages

        return render(request, 'SceneTagSite/update_shot.html',
                      {
                          'video': video,
                          'fps': fps,
                          'shots': shots,
                          'cur_shotpage': cur_shotpage,
                          'max_shotpage': max_shotpage,
                      })


def extract_current_frame(request):
    response_datas = {
        'save_status': False,
    }
    video_pk = int(request.GET['video_pk'])
    currentFrame = int(request.GET['currentFrame'])
    currentTimeStamp = request.GET['currentTimeStamp']

    video = models.Video.objects.get(pk=video_pk)
    video_path = video.localFile.path
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)

    count = 0
    total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    total_frames = int(total_frames)

    while vidcap.isOpened():
        frame_exists, curr_frame = vidcap.read()
        if frame_exists:
            if count == int(currentFrame):
                t_s = (vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                diff = abs(float(t_s) - float(currentTimeStamp))
                if diff < 1:
                    capture_path = os.path.join(settings.MEDIA_ROOT, str(video_pk), u"output")
                    img_name = u'_frame%d.jpg' % count
                    if os.path.exists(capture_path):
                        final_path = os.path.join(capture_path, img_name)
                    else:
                        os.makedirs(capture_path)
                        final_path = os.path.join(capture_path, img_name)
                    # width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    # height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    curr_frame = cv2.resize(curr_frame, (724, 408))
                    save_status = cv2.imwrite(final_path, curr_frame)
                    if save_status:
                        response_datas['save_status'] = True

        count += 1
        if count >= total_frames:
            break
    vidcap.release()
    print(img_name)

    new_frame = models.FrameList(video=video, framerate=fps, currentFrame=currentFrame, imgName=img_name)
    new_frame.save()

    return HttpResponse(json.dumps(response_datas), content_type="application/json")


def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def get_key_frame_list(video_id):
    imgs = []
    work_root = os.path.join(settings.MEDIA_ROOT, str(video_id), u"output")

    filenames = os.listdir(work_root)
    for filename in filenames:
        full_filename = os.path.join(work_root, filename)
        if not os.path.isdir(full_filename):
            filename = filename.split('.')
            imgs.append(filename[0])
    imgs.sort(key=alphanum_key)

    return imgs


def key_frame_list(request, video_id):
    video = models.Video.objects.get(pk=video_id)
    frames = models.FrameList.objects.filter(video__pk=video_id).order_by('currentTimeStamp')
    # imgs = get_key_frame_list(video_id)
    vid = cv2.VideoCapture(video.localFile.path)
    fps = vid.get(cv2.CAP_PROP_FPS)

    return render(request, 'SceneTagSite/frame_list.html', {
        'video': video,
        # 'imgs': imgs,
        'frames': frames,
        'fps': fps,
    })


def update_frames(request, video_id, page_num):
    video = models.Video.objects.get(pk=video_id)
    frame_list = models.FrameList.objects.filter(video=video, shot__isnull=True).order_by('currentFrame')
    imgs = get_key_frame_list(video_id)
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


def ajax_get_frame_url(request):
    response_datas = []

    if request.GET['name'] == 'getFrameURL':
        response_data = {}
        videoNum = int(request.GET['videoNum'])
        frameNum = int(request.GET['frameNum'])
        video = models.Video.objects.get(pk=videoNum)
        response_data['tagID'] = request.GET['tagID']
        response_data['URL'] = frame_extractor.get_frame_url(videoNum, video.localFile.path, frameNum)

    response_datas.append(response_data)
    return HttpResponse(json.dumps(response_datas), content_type="application/json")


def frames_grouping(request):
    response_datas = {
        "reload_url": '',
        "number_of_frame": 0,
    }
    if request.GET['name'] == 'frameGrouping':
        framePK = request.GET['framePK']
        videoPK = request.GET['videoPK']
        clicked_frames = models.FrameList.objects.filter(id__lte=framePK, shot__isnull=True, video__id=videoPK)
        number_of_frame = len(clicked_frames)  # grouping 된 갯수
        start_frame = clicked_frames[0].currentFrame
        start_timestamp = clicked_frames[0].currentTimeStamp

        last_element = clicked_frames.order_by('-pk')[0]
        end_frame = last_element.currentFrame
        end_timestamp = last_element.currentTimeStamp

        models.make_new_frame(videoPK, number_of_frame, start_frame, end_frame, start_timestamp, end_timestamp)
        response_datas['reload_url'] = request.GET['reload_url']
        response_datas['number_of_frame'] = number_of_frame
    return HttpResponse(json.dumps(response_datas), 'application/json')


def export_object_tag_csv(request, video_id):
    videos = models.Video.objects.get(pk=video_id).programName

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(videos + '_object_tag')

    writer = csv.writer(response)
    writer.writerow(['imgName', 'imgWidth', 'imgHeight', 'x1', 'y1', 'w', 'h'])

    object_tags = models.ObjectTag.objects.filter(video__pk=video_id).values_list('imgName', 'imgWidth', 'imgHeight',
                                                                                  'x1', 'y1', 'w', 'h')
    for tag in object_tags:
        writer.writerow(tag),

    return response


@csrf_exempt
def object_tagging(request, video_id, frame_id):
    video = models.Video.objects.get(pk=video_id)
    frame = models.FrameList.objects.get(pk=frame_id)
    img_name = models.FrameList.objects.get(pk=frame_id).imgName
    currenttime = models.FrameList.objects.get(pk=frame_id).currentTimeStamp

    test2 = datetime.strptime('2019-7-20 ' + currenttime, '%Y-%m-%d %H:%M:%S.%f')

    current = time.mktime(test2.timetuple()) + test2.microsecond / 1e6
    time_dt = current * 1000

    im = cv2.imread(os.path.join(settings.MEDIA_ROOT, str(video_id), u"output", img_name))
    if request.method == 'POST':
        x = request.POST['x1']
        y = request.POST['y1']
        w = request.POST['w']
        h = request.POST['h']
        label = request.POST['label']

        new_object_tag = ObjectTag(video=video,
                                   frame=frame,
                                   imgName=img_name,
                                   imgWidth=im.shape[1],
                                   imgHeight=im.shape[0],
                                   x1=x,
                                   y1=y,
                                   w=w,
                                   h=h,
                                   label=label)
        new_object_tag.save()
        return redirect('object_tagging', video_id, frame_id)

    img_url = '/videos/{}/output/{}'.format(str(video_id), img_name)
    object_tags = ObjectTag.objects.filter(video=video_id, frame=frame_id).order_by('-lastSavedDateTime')

    form = ObjectTagForm
    # canvas
    query_length_object = len(object_tags)
    list_x_object = []
    list_y_object = []
    list_w_object = []
    list_h_object = []
    list_label_object = []
    list_id_object = []

    for i in range(0, query_length_object):
        list_x_object.append(object_tags[i].x1)
        list_y_object.append(object_tags[i].y1)
        list_w_object.append(object_tags[i].w)
        list_h_object.append(object_tags[i].h)
        list_label_object.append(object_tags[i].get_label_display())
        list_id_object.append(object_tags[i].pk)

    return render(request, 'SceneTagSite/object_tagging.html', {
        'video': video,
        'frame': frame,
        'img_url': img_url,
        'object_tags': object_tags,
        'form': form,

        # canvas
        'list_x_object': list_x_object,
        'list_y_object': list_y_object,
        'list_w_object': list_w_object,
        'list_h_object': list_h_object,
        'list_label_object': list_label_object,
        'list_id_object': list_id_object,
        'query_length_object': query_length_object,
    })


def del_object_tagging(request, video_id, tag_pk):
    tag = ObjectTag.objects.get(pk=tag_pk)
    img_name = tag.frame_id
    tag.delete()
    return HttpResponseRedirect(reverse('object_tagging', args=(video_id, img_name)))


def get_data(request):  # test

    video_pk = int(request.GET['video_pk'])
    objecttag_1 = models.ObjectTag.objects.filter(video__pk=video_pk, label="1")
    objecttag_2 = models.ObjectTag.objects.filter(video__pk=video_pk, label="2")
    objecttag_3 = models.ObjectTag.objects.filter(video__pk=video_pk, label="3")
    objecttag_4 = models.ObjectTag.objects.filter(video__pk=video_pk, label="4")
    objecttag_5 = models.ObjectTag.objects.filter(video__pk=video_pk, label="5")
    objecttag_6 = models.ObjectTag.objects.filter(video__pk=video_pk, label="6")
    objecttag_7 = models.ObjectTag.objects.filter(video__pk=video_pk, label="7")

    query_length_tag_1 = len(objecttag_1)
    query_length_tag_2 = len(objecttag_2)
    query_length_tag_3 = len(objecttag_3)
    query_length_tag_4 = len(objecttag_4)
    query_length_tag_5 = len(objecttag_5)
    query_length_tag_6 = len(objecttag_6)
    query_length_tag_7 = len(objecttag_7)

    object_list_1 = []
    object_list_2 = []
    object_list_3 = []
    object_list_4 = []
    object_list_5 = []
    object_list_6 = []
    object_list_7 = []

    for i in range(0, query_length_tag_1):
        object_list_1.append(objecttag_1[i].currenttime)
        object_list_1.append(objecttag_1[i].imgName)

    for i in range(0, query_length_tag_2):
        object_list_2.append(objecttag_2[i].currenttime)
        object_list_2.append(objecttag_2[i].imgName)

    for i in range(0, query_length_tag_3):
        object_list_3.append(objecttag_3[i].currenttime)
        object_list_3.append(objecttag_3[i].imgName)

    for i in range(0, query_length_tag_4):
        object_list_4.append(objecttag_4[i].currenttime)
        object_list_4.append(objecttag_4[i].imgName)

    for i in range(0, query_length_tag_5):
        object_list_5.append(objecttag_5[i].currenttime)
        object_list_5.append(objecttag_5[i].imgName)

    for i in range(0, query_length_tag_6):
        object_list_6.append(objecttag_6[i].currenttime)
        object_list_6.append(objecttag_6[i].imgName)

    for i in range(0, query_length_tag_7):
        object_list_7.append(objecttag_7[i].currenttime)
        object_list_7.append(objecttag_7[i].imgName)

    test_data = {
        'object_list_1': object_list_1,
        'object_list_2': object_list_2,
        'object_list_3': object_list_3,
        'object_list_4': object_list_4,
        'object_list_5': object_list_5,
        'object_list_6': object_list_6,
        'object_list_7': object_list_7,

        # object 개수
        'query_length_tag_1': query_length_tag_1,
        'query_length_tag_2': query_length_tag_2,
        'query_length_tag_3': query_length_tag_3,
        'query_length_tag_4': query_length_tag_4,
        'query_length_tag_5': query_length_tag_5,
        'query_length_tag_6': query_length_tag_6,
        'query_length_tag_7': query_length_tag_7,
    }
    return JsonResponse(test_data)


def auto_object_tagging(request, video_id, frame_id):
    video = models.Video.objects.get(pk=video_id)
    frame = models.FrameList.objects.get(pk=frame_id)
    img_name = models.FrameList.objects.get(pk=frame_id).imgName
    img_url = '/videos/{}/output/{}'.format(str(video_id), img_name)

    object_tag_result_place = models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id,
                                                                    manual_module_name='korea.place').values_list(
        'manual_description').annotate(total=Sum('manual_score')).order_by('-total')[:5]
    object_tag_result_face = models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id,
                                                                   manual_module_name='korea.face').values_list(
        'manual_description').annotate(total=Sum('manual_score')).order_by('-total')[:5]
    object_tag_result_object = Counter(models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id,
                                                                             manual_module_name='object').values_list(
        'manual_description', flat=True))
    object_tag_result_object = object_tag_result_object.most_common(5)

    return render(request, 'SceneTagSite/auto_tagging.html', {
        'video': video,
        'frame': frame,
        'img_url': img_url,
        'object_tag_result_place': object_tag_result_place,
        'object_tag_result_face': object_tag_result_face,
        'object_tag_result_object': object_tag_result_object,
    })


def object_tag_info_json(request, video_id, frame_id):
    video = models.Video.objects.filter(pk=video_id)
    frame = models.FrameList.objects.filter(pk=frame_id)
    object_tag_result_place = models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id,
                                                                    manual_module_name='korea.place')
    object_tag_result_face = models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id,
                                                                   manual_module_name='korea.face')
    object_tag_result_object = Counter(
        models.ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id, manual_module_name='object'))

    retdata = {}

    data = serializers.serialize('json', video)
    retdata['video'] = data

    data = serializers.serialize('json', frame)
    retdata['frame'] = data

    data = serializers.serialize('json', object_tag_result_place)
    retdata['object_tag_result_place'] = data

    data = serializers.serialize('json', object_tag_result_face)
    retdata['object_tag_result_face'] = data

    data = serializers.serialize('json', object_tag_result_object)
    retdata['object_tag_result_object'] = data

    return JsonResponse(retdata)


def auto_object_tagging_register(request, video_id, frame_id):
    video = models.Video.objects.get(pk=video_id)
    frame = models.FrameList.objects.get(pk=frame_id)
    form = ObjectTaggingForm(request.POST, request.FILES)

    if request.method == 'POST':
        if form.is_valid():
            object_tag = AutoObjectTag()
            object_tag.video = form.cleaned_data['video']
            object_tag.frame = form.cleaned_data['frame']
            object_tag.threshold = form.cleaned_data['threshold']
            object_tag.module_name = form.cleaned_data['module_name']
            object_tag.save()
            return redirect('auto_object_tagging', video_id, frame_id)
    else:
        form = ObjectTaggingForm()
    return render(request, 'SceneTagSite/auto_tagging_register.html', {
        'form': form,
        'video': video,
        'frame': frame,
    })


def auto_object_tagging_modify(request, video_id, frame_id):
    ResultTagFormSet = modelformset_factory(ManualTagResult, form=ResultTagForm, extra=0)
    formset = ResultTagFormSet(request.POST or None,
                               queryset=ManualTagResult.objects.filter(manual_tag_result__frame__pk=frame_id))
    if formset.is_valid():
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        return redirect('auto_object_tagging', video_id, frame_id)
    return render(request, 'SceneTagSite/auto_tagging_modify.html', {
        'formset': formset,
    })


def shot_rotation(request, video_id, shot_id):
    video = models.Video.objects.get(pk=video_id)
    shot = models.Shot.objects.get(pk=shot_id)
    form = ShotRotationForm(request.POST, request.FILES)

    if request.method == "POST":
        if form.is_valid():
            shot_rota = ShotRotation()
            shot_rota.video = form.cleaned_data['video']
            shot_rota.shot = form.cleaned_data['shot']
            shot_rota.rotation = form.cleaned_data['rotation']
            shot_rota.parameter = form.cleaned_data['parameter']
            shot_rota.save()
            return redirect('shot_list', video_id)
    else:
        form = ShotRotationForm()
        return render(request, 'SceneTagSite/shot_rotation_register.html', {
            'video': video,
            'shot': shot,
            'form': form,
        })
