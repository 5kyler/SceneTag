from __future__ import unicode_literals
from django.contrib import admin
from SceneTagSite import models

# Register your models here.
admin.site.register(models.Video)
admin.site.register(models.Shot)
admin.site.register(models.FrameList)
admin.site.register(models.ShotRotation)
admin.site.register(models.ObjectTag)
admin.site.register(models.AutoObjectTag)
admin.site.register(models.AutoTagResult)