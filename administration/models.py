from django.db.models import Q
from django.contrib.auth.models import User


def render_user(self):
    if self.first_name and self.last_name:
        return "%s %s (%s) <%s>%s" % (self.first_name, self.last_name, self.username, self.email, (" - administrateur" if self.is_staff else ""))

    return "%s <%s>%s" % (self.username, self.email, (" - administrateur" if self.is_staff else ""))


User.__unicode__ = render_user

def users_can_administrate(self):
    groups_managed_by_user = self.groups_managed_by_user()
    return User.objects.filter(Q(group_is_admin_set__in=groups_managed_by_user)|Q(group_is_member_set__in=groups_managed_by_user))


User.users_can_administrate = users_can_administrate
User.groups_managed_by_user = lambda self: self.group_is_admin_set.all()
