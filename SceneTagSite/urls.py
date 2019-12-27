from django.urls import path, include
from django.contrib import admin

from SceneTagSite import views

urlpatterns = [
    path('test/', views.test, name='test'),
]