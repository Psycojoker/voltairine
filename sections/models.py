from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


class Section(MPTTModel):
    title = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.title

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
