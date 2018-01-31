from django.db import models
from django.contrib.auth.models import User

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from mptt.utils import tree_item_iterator


class SectionQuerySet(models.QuerySet):
    def as_python_tree(self):
        iterator = tree_item_iterator(self)
        first = True

        current = []
        stack = [current]
        for row, infos in iterator:
            if infos["new_level"] and not first:
                stack.append(current)
                current = current[-1][1]

            current.append([row, []])

            first = False

            for i in infos["closed_levels"]:
                if stack:
                    current = stack.pop()

        return current


class SectionManager(TreeManager):
    def get_queryset(self):
        return SectionQuerySet(self.model, using=self._db).order_by(self.tree_id_attr, self.left_attr)


class Section(MPTTModel):
    objects = SectionManager()

    title = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    notification_email = models.EmailField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    def display_level_indicator(self):
        return "--" * self.level

    class MPTTMeta:
        order_insertion_by = ['title']


class Permission(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)

    class Meta:
        unique_together = (('user', 'section'),)


class VideoSection(models.Model):
    video = models.OneToOneField("video.Video")
    section = models.ForeignKey(Section)

    class Meta:
        unique_together = (('video', 'section'),)

    def __unicode__(self):
        return self.section.__unicode__()
