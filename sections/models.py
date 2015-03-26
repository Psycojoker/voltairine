from django.db import models
from django.contrib.auth.models import User

from mptt.models import MPTTModel, TreeForeignKey
from mptt.utils import tree_item_iterator


class Section(MPTTModel):
    title = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.title

    @staticmethod
    def as_python_tree(queryset):
        iterator = tree_item_iterator(queryset)
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
                current = stack.pop()

        return current

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
