# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-26 15:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video_share', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videoshare',
            name='random_id',
        ),
        migrations.AddField(
            model_name='videoshare',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='videoshare',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]