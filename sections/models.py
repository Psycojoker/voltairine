from django.db import models
from django.contrib.auth.models import User


class SubSection(models.Model):
    title = models.CharField(max_length=255)
    section = models.CharField(max_length=1, choice=((('1', 'Tournages'), ('2', 'Montages'), ('3', 'Producteurs'))))


class SubSubSection(models.Model):
    title = models.CharField(max_length=255)
    subsection = models.ForeignKey(SubSection)


class Permissoins(models.Model):
    user = models.ForeignKey(User)
    subsection = models.ForeignKey(SubSection, null=True)
    subsubsection = models.ForeignKey(SubSubSection, null=True)
