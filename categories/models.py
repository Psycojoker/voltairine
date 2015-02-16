from django.db import models


class SubSection(models.Model):
    title = models.CharField(max_length=255)
    section = models.CharField(max_length=1, choice=((('1', 'Tournages'), ('2', 'Montages'), ('3', 'Producteurs'))))


class SubSubSection(models.Model):
    title = models.CharField(max_length=255)
    subsection = models.ForeignKey(SubSection)
