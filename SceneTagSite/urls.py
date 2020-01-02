from django.urls import path, include
from django.contrib import admin

from SceneTagSite import views

urlpatterns = [

    # video list page
    path('list/page/<list_page>/', views.video_list, name='list'),
    path('list/refresh/', views.video_list_refresh, name='refresh_list'),

    # video shot_list
    path('list/shot/<video_id>/', views.shot_list, name='shot_list'),

    # frame_list
    path('list/frame/<video_id>/', views.frame_list, name='frame_list'),

    #ajax
    path('ajax/extract_current_frame', views.extract_current_frame, name='extract_current_frame')
]