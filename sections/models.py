from django.db import models
from django.contrib.auth.models import User


class SubSection(models.Model):
    title = models.CharField(max_length=255)
    section = models.CharField(max_length=1, choices=((('1', 'Tournages'), ('2', 'Montages'), ('3', 'Producteurs'))))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class SubSubSection(models.Model):
    title = models.CharField(max_length=255)
    subsection = models.ForeignKey(SubSection)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Permissoins(models.Model):
    user = models.ForeignKey(User)
    subsection = models.ForeignKey(SubSection, null=True)
    subsubsection = models.ForeignKey(SubSubSection, null=True)
