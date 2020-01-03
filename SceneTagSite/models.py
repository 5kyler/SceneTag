from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from SceneTagSite.utils.converter import TimeConverter


# Create your models here.

class Video(models.Model):
    programName = models.CharField(max_length=255)
    localFile = models.FileField(blank=True)
    registerDateTime = models.DateTimeField(default=timezone.now)
    lastSavedDateTime = models.DateTimeField(default=timezone.now)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    framerate = models.FloatField(default=29.97)
    pgm_tms_id = models.CharField(max_length=255, default=0)

    def __unicode__(self):
        return self.programName

    def save(self, *args, **kwargs):
        self.lastSavedDateTime = timezone.now()
        super(Video, self).save(*args, **kwargs)


class Shot(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    number_of_frame = models.IntegerField
    startFrame = models.IntegerField(default=0)
    endFrame = models.IntegerField(default=0)
    startTimeStamp = models.CharField(max_length=255, blank=True)
    endTimeStamp = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        name = str(self.video.programName) + u'Shot(' + str(self.pk) + u')'
        return name


class FrameList(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    shot = models.ForeignKey(Shot, on_delete=models.SET_NULL, blank=True, null=True)
    framerate = models.FloatField(default=29.97)
    currentFrame = models.IntegerField(default=0)
    currentTimeStamp = models.CharField(max_length=255, blank=True)

    def make_timestamp(self, frame, framerate):
        tc = TimeConverter(frame_rate=framerate)
        tc.set_framenum(frame)
        return tc.get_timestamp()

    def save(self, *args, **kwargs):
        self.currentTimeStamp = self.make_timestamp(frame=(self.currentFrame * self.framerate),
                                                    framerate=self.framerate)
        super(FrameList, self).save(*args, **kwargs)

    def __unicode__(self):
        name = u'frame_pk:' + str(self.pk)
        return name
