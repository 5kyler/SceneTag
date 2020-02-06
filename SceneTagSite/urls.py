from django.urls import path, include
from django.contrib import admin

from SceneTagSite import views

urlpatterns = [

    # video list page
    path('list/page/<list_page>/', views.video_list, name='list'),
    path('list/refresh/', views.video_list_refresh, name='refresh_list'),

    # video shot_list
    # path('list/shot/<video_id>/', views.shot_list, name='shot_list'),

    # frame_list
    path('frame/<video_id>/', views.FrameBrowse.as_view(), name='frame_list'),
    path('frame/<video_id>/page/<page_num>/', views.FrameBrowse.as_view(), name='frame_update'),

    # shot_list
    path('shot/<video_id>/', views.ShotBrowse.as_view(), name='shot_list'),
    path('shot/<video_id>/page/<page_num>/', views.ShotBrowse.as_view(), name='shot_update'),

    # from rotation register
    path('rotation/<video_id>/shot/<shot_id>/', views.shot_rotation, name='shot_rotation'),

    # get_img
    path('extract_current_frame/<video_id>/', views.extract_current_frame, name='extract_current_frame'),
    path('ajax/get_frame/', views.ajax_get_frame_url, name='ajax_get_frame'),
    path('utils/image/', views.ajax_get_frame_url, name='util_media_image'),

    # frame grouping
    path('ajax/frames_grouping/', views.frames_grouping, name='frames_grouping'),
]