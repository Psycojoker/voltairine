from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    film_name = models.CharField(max_length=255, null=True, blank=True)
    realisation = models.CharField(max_length=255, null=True, blank=True)
    production = models.CharField(max_length=255, null=True, blank=True)
    photo_direction = models.CharField(max_length=255, null=True, blank=True)
    observations = models.TextField(null=True, blank=True)

    # montage_date = models.DateField(null=True)
    # montage_version = models.CharField(max_length=255)
    # bar_code_lto_saya = models.CharField(max_length=255)
    # bar_code_lto_prod = models.CharField(max_length=255)
