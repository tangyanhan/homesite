# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

from video.models import Video

class CustomUser(AbstractUser):
    rating = models.PositiveIntegerField(default=Video.G)

    # custom save model
    def save(self, *args, **kwargs):
        # figure out warranty end date
        if self.is_superuser:
            self.rating = Video.P
        super(CustomUser, self).save()
