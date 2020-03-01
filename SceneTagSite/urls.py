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
    path('frame/<video_id>/', views.key_frame_list, name='frame_list'),
    path('frame/<video_id>/page/<page_num>/', views.update_frames, name='frame_update'),

    # shot_list
    path('shot/<video_id>/', views.ShotBrowse.as_view(), name='shot_list'),
    path('shot/<video_id>/page/<page_num>/', views.ShotBrowse.as_view(), name='shot_update'),

    # from rotation register
    path('rotation/<video_id>/shot/<shot_id>/', views.shot_rotation, name='shot_rotation'),

    # get_img
    path('extract_current_frame/', views.extract_current_frame, name='extract_current_frame'),
    path('ajax/get_frame/', views.ajax_get_frame_url, name='ajax_get_frame'),
    path('utils/image/', views.ajax_get_frame_url, name='util_media_image'),

    # frame grouping
    path('ajax/frames_grouping/', views.frames_grouping, name='frames_grouping'),

    # object tagging
    path('tag/<video_id>/<frame_id>/', views.object_tagging, name='object_tagging'),
    path('delete/<video_id>/<tag_pk>/', views.del_object_tagging, name='del_object_tagging'),

    # auto tagging
    path('<video_id>/auto_tag/<frame_id>/json', views.object_tag_info_json, name='object_tag_json'),
    path('<video_id>/auto_tag/<frame_id>/', views.auto_object_tagging, name='auto_object_tagging'),
    path('<video_id>/auto_tag/<frame_id>/register/', views.auto_object_tagging_register, name='auto_object_tagging_register'),
    path('<video_id>/auto_tag/<frame_id>/modify/', views.auto_object_tagging_modify, name='auto_object_tagging_modify'),
    # csv
    path('export/<video_id>/object/csv/', views.export_object_tag_csv, name='export_object_tag_csv'),

    #ajax
    path('ajax/get_data/', views.get_data, name='api-data'),
]
