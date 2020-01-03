from __future__ import unicode_literals
from django.contrib import admin
from SceneTagSite import models

# Register your models here.
admin.site.register(models.Video)
admin.site.register(models.Shot)
admin.site.register(models.FrameList)