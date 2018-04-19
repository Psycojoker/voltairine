from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Lower

from sections.models import Section


class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")

    admins = models.ManyToManyField(User, related_name="group_is_admin_set", verbose_name="Administrateurs", blank=True)
    users = models.ManyToManyField(User, related_name="group_is_member_set", verbose_name="Utilisateurs", blank=True)

    permissions = models.ManyToManyField(Section)

    can_download = models.BooleanField(default=False)

    def get_permissions(self):
        if not hasattr(self, "_permissions_cache"):
            self._permissions_cache = self.permissions.all()
        return self._permissions_cache

    def __unicode__(self):
        return self.name

    def get_admins(self):
        return self.admins.order_by(Lower("email"), Lower("first_name"), Lower("last_name"), Lower("username"))

    def get_users(self):
        return self.users.order_by(Lower("email"), Lower("first_name"), Lower("last_name"), Lower("username"))
