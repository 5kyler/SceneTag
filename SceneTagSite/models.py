from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from SceneTagSite.utils.converter import TimeConverter


# Create your models here.

def make_new_frame(video_pk, number_of_frame, start_frame, end_frame, start_timestamp, end_timestamp):
    video = Video.objects.get(pk=video_pk)
    frames = FrameList.objects.filter(video__pk=video_pk, currentFrame__gte=start_frame, currentFrame__lte=end_frame)
    new_shot = Shot(video=video)
    new_shot.number_of_frame = number_of_frame
    new_shot.startFrame = start_frame
    new_shot.endFrame = end_frame
    new_shot.startTimestamp = start_timestamp
    new_shot.endTimestamp = end_timestamp
    new_shot.save()

    for frame in frames:
        frame.shot = new_shot
        frame.save()


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
    attack = models.CharField(max_length=255, default='Normal')

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
        self.currentTimeStamp = self.make_timestamp(frame=int(self.currentFrame), framerate=int(self.framerate))
        super(FrameList, self).save(*args, **kwargs)

    def __unicode__(self):
        name = u'frame_pk:' + str(self.pk)
        return name
