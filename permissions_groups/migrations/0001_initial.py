# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Nom')),
                ('admins', models.ManyToManyField(related_name='group_is_admin_set', verbose_name=b'Administrateurs', to=settings.AUTH_USER_MODEL, blank=True)),
                ('permissions', models.ManyToManyField(to='sections.Section')),
                ('users', models.ManyToManyField(related_name='group_is_member_set', verbose_name=b'Utilisateurs', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
    ]
