from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from sections.models import Section
from sections.utils import unfold_tree

from video.models import Video


def render_user(self):
    if self.first_name and self.last_name:
        return "%s %s (%s) <%s>%s" % (self.first_name, self.last_name, self.username, self.email, (" - administrateur" if self.is_staff else ""))

    return "%s <%s>%s" % (self.username, self.email, (" - administrateur" if self.is_staff else ""))


User.__unicode__ = render_user

def users_can_administrate(self):
    groups_managed_by_user = self.groups_managed_by_user()
    return User.objects.filter(Q(group_is_admin_set__in=groups_managed_by_user)|Q(group_is_member_set__in=groups_managed_by_user))


def sections_can_administrate(self):
    sections_of_groups = Section.objects.filter(group__admins=self)

    sections_tree = Section.objects.all().as_python_tree()
    node_to_childrens = unfold_tree(sections_tree)

    return set(list(sections_of_groups) + sum([node_to_childrens[x] for x in sections_of_groups], []))


def videos_can_administrate(self):
    return Video.objects.filter(videosection__section__in=map(lambda x: x.pk, self.sections_can_administrate()))


def all_groups(self):
    for i in self.group_is_admin_set.all():
        i.is_admin = True
        yield i

    for i in self.group_is_member_set.all():
        i.is_admin = False
        yield i


def can_download(self):
    if not hasattr(self, "useradditionalattributes"):
        self.useradditionalattributes = UserAdditionalAttributes.objects.create(user=self)

    return self.useradditionalattributes.can_download

def can_download_setter(self, value):
    if not hasattr(self, "useradditionalattributes"):
        self.useradditionalattributes = UserAdditionalAttributes.objects.create(user=self)

    self.useradditionalattributes.can_download = value


def can_see_download_button(self):
    if self.is_superuser:
        return True

    if self.is_staff:
        return True

    if self.can_download:
        return True

    # XXX check that the video is in a group that can see it
    # but that looks overkill here
    for group in self.group_is_admin_set.all():
        if group.can_download:
            return True

    for group in self.group_is_member_set.all():
        if group.can_download:
            return True

    return False


class UserAdditionalAttributes(models.Model):
    user = models.OneToOneField(User)
    can_download = models.BooleanField(default=False)


User.users_can_administrate = users_can_administrate
User.groups_managed_by_user = lambda self: self.group_is_admin_set.all()
User.sections_can_administrate = sections_can_administrate
User.videos_can_administrate = videos_can_administrate
User.all_groups = all_groups
User.can_download = property(can_download, can_download_setter)
User.can_see_download_button = can_see_download_button
