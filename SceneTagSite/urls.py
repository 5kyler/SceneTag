from django.urls import path, include
from django.contrib import admin

from SceneTagSite import views

urlpatterns = [
    path('test/', views.test, name='test'),

    # video list page
    path('list/page/<list_page>/', views.video_list, name='list'),
    path('list/refresh/', views.video_list_refresh, name='refresh_list'),

    # video page
    path('view/<video_id>/', views.video, name='video_view'),

    # edit video
    path('edit/<video_id>/', views.edit_video, name='edit_video'),

    #ajax
    path('ajax/extract_current_frame', views.extract_current_frame, name='extract_current_frame')
]