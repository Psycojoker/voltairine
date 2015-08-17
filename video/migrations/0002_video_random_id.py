# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.db import models, migrations


def generate_id_for_videos(apps, schema_editor):
    Video = apps.get_model("video", "Video")

    for video in Video.objects.all():
        video.random_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
        video.save()


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='random_id',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=False,
        ),
        migrations.RunPython(generate_id_for_videos, lambda apps, schema_editor: None),
        migrations.AlterField(
            model_name='video',
            name='random_id',
            field=models.CharField(unique=True, max_length=20, db_index=True, null=False, blank=False),
            preserve_default=False,
        ),
    ]
