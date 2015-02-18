from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    film_name = models.CharField(max_length=255)
    realisation = models.CharField(max_length=255)
    production = models.CharField(max_length=255)
    photo_direction = models.CharField(max_length=255)
    observations = models.TextField()

    # montage_date = models.DateField(null=True)
    # montage_version = models.CharField(max_length=255)
    # bar_code_lto_saya = models.CharField(max_length=255)
    # bar_code_lto_prod = models.CharField(max_length=255)
