# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('file_name', models.CharField(max_length=255)),
                ('thumbnail_name', models.CharField(max_length=255, null=True, blank=True)),
                ('film_name', models.CharField(max_length=255, null=True, blank=True)),
                ('realisation', models.CharField(max_length=255, null=True, blank=True)),
                ('production', models.CharField(max_length=255, null=True, blank=True)),
                ('photo_direction', models.CharField(max_length=255, null=True, blank=True)),
                ('lto_archive_number', models.CharField(max_length=255, null=True, blank=True)),
                ('observations', models.TextField(null=True, blank=True)),
                ('additional_infos', jsonfield.fields.JSONField(default={})),
            ],
        ),
    ]
