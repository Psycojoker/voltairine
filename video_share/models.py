# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from video.models import Video


class VideoShare(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    video = models.ForeignKey(Video)
    user = models.ForeignKey(User, null=True, blank=True)
