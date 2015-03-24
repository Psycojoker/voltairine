from django.db import models
from django.contrib.auth.models import User

from sections.models import Section


class Group(models.Model):
    name = models.CharField(max_length=255)

    admins = models.ManyToManyField(User, related_name="group_is_admin_set")
    users = models.ManyToManyField(User, related_name="group_is_member_set")

    permissions = models.ManyToManyField(Section)
