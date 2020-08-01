import os
import uuid

from django.db import models

# Create your models here.
from django.utils.text import slugify


def upload_handler(instance, filename, folder=None):
    filename_base, filename_ext = os.path.splitext(filename)

    # if folder:
    #     bucket_url = "media/{folder}/{filename}-small{extension}".format(
    #         filename=slugify(instance.title),
    #         extension=filename_ext.lower(),
    #         folder=folder
    #     )
    # else:
    #     bucket_url = "media/{filename}-small{extension}".format(
    #         filename=slugify(instance.title),
    #         extension=filename_ext.lower(),
    #     )
    #
    # if folder:
    #     if not os.path.exists("media/{}".format(folder)):
    #         os.makedirs("media/{}".format(folder))
    # # checks to see if gae environment is enabled

    return "media/{titlename}_{filename}{extension}".format(
        titlename=slugify(instance.title),
        filename=filename_base,
        extension=filename_ext.lower(),
    )


class MediaManager(models.Model):
    MEDIA_TYPES = [
        ('sheet', 'sheet'),
    ]

    title = models.CharField(
        max_length=2000, help_text='Media file title', default="")
    type = models.CharField(max_length=255, choices=MEDIA_TYPES, default="sheet")
    media_file = models.FileField(
        upload_to=upload_handler, help_text='Upload media file', max_length=2000)
    url = models.URLField(
        null=True, blank=True, help_text='Media url will be populated after uploading file.')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
