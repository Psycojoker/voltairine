import os
import av

from django.db import models
from django.conf import settings

from jsonfield import JSONField


class Video(models.Model):
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    film_name = models.CharField(max_length=255, null=True, blank=True)
    realisation = models.CharField(max_length=255, null=True, blank=True)
    production = models.CharField(max_length=255, null=True, blank=True)
    photo_direction = models.CharField(max_length=255, null=True, blank=True)
    observations = models.TextField(null=True, blank=True)

    # montage_date = models.DateField(null=True)
    # montage_version = models.CharField(max_length=255)
    # bar_code_lto_saya = models.CharField(max_length=255)
    # bar_code_lto_prod = models.CharField(max_length=255)

    additional_infos = JSONField()

    @property
    def duration(self):
        if "duration" not in self.additional_infos:
            self.additional_infos["duration"] = av.open(os.path.join(settings.MEDIA_ROOT, "videos", self.file_name.encode("Utf-8"))).duration
            self.save()

        video_duration = float(self.additional_infos["duration"]) / av.time_base
        minutes, seconds = divmod(video_duration, 60)

        if video_duration > 60 * 60:
            hours, minutes = divmod(minutes, 60)

            return "%d:%.2d:%.2d" % (hours, minutes, seconds)

        return "%d:%.2d" % (minutes, seconds)

    def __unicode__(self):
        return self.title
