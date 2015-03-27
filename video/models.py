import os
import av

from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify

from jsonfield import JSONField


class Video(models.Model):
    title = models.CharField(max_length=255)

    file_name = models.CharField(max_length=255)
    thumbnail_name = models.CharField(max_length=255, null=True, blank=True)

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
    def absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, "videos", self.file_name.encode("Utf-8"))


    @property
    def thumbnail_uri(self):
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
        if not os.path.exists(thumbnails_dir):
            os.makedirs(thumbnails_dir)

        if not self.thumbnail_name or not os.path.exists(os.path.join(thumbnails_dir, self.thumbnail_name)):
            self.thumbnail_name = slugify(".".join(self.file_name.split(".")[:-1])) + ".png"

            image = self._generate_thumbnail_image_from_video()

            image.resize((230, 146)).save(os.path.join(thumbnails_dir, self.thumbnail_name))
            self.save()

        return os.path.join(settings.MEDIA_URL, "thumbnails", self.thumbnail_name)

    def _generate_thumbnail_image_from_video(self):
        video = av.open(self.absolute_path)

        image = None
        until_2_seconds = 0

        for i in video.demux():
            for frame in i.decode():
                if frame.__class__.__name__ == "VideoFrame":
                    if until_2_seconds > self.fps * 2:  # ~2 seconds
                        image = frame.to_image()
                        break
                    until_2_seconds += 1
            if image is not None:
                break

        return image

    @property
    def duration(self):
        if "duration" not in self.additional_infos:
            self.additional_infos["duration"] = av.open(self.absolute_path).duration
            self.save()

        video_duration = float(self.additional_infos["duration"]) / av.time_base
        minutes, seconds = divmod(video_duration, 60)

        if video_duration > 60 * 60:
            hours, minutes = divmod(minutes, 60)

            return "%d:%.2d:%.2d" % (hours, minutes, seconds)

        return "%d:%.2d" % (minutes, seconds)

    @property
    def width_x_height(self):
        if "height" not in self.additional_infos or "width" not in self.additional_infos:
            # video stream always appears to be the first one, I'm not convinced that it's always the case
            self.additional_infos["height"] = av.open(self.absolute_path).streams[0].height
            self.additional_infos["width"] = av.open(self.absolute_path).streams[0].width
            self.save()

        return "%sx%s" % (self.additional_infos["width"], self.additional_infos["height"])

    @property
    def file_size(self):
        def sizeof_fmt(num):
            for unit in ['','K','M','G','T','P','E','Z']:
                if abs(num) < 1024.0:
                    return "%3.1f%so" % (num, unit)
                num /= 1024.0
            return "%.1f%so" % (num, 'Y')

        if "file_size" not in self.additional_infos:
            self.additional_infos["file_size"] = av.open(self.absolute_path).size
            self.save()

        return sizeof_fmt(self.additional_infos["file_size"])

    @property
    def fps(self):
        if "fps" not in self.additional_infos:
            video = av.open(self.absolute_path)
            video_stream = video.streams[0]
            self.additional_infos["fps"] = video_stream.frames / (float(video.duration) / av.time_base)
            self.save()

        return self.additional_infos["fps"]

    def __unicode__(self):
        return self.title
