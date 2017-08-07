from __future__ import unicode_literals

from django.db import models

KEYWORD_MAX_LENGTH = 100


class Video(models.Model):
    video_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=256, default='')
    path = models.CharField(max_length=1024)
    duration = models.PositiveSmallIntegerField(null=True)  # 0-32767 in seconds, about 9 hours at max
    import_date = models.DateField(null=True, auto_now=True)  # Date when it's imported
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    watch_count = models.PositiveIntegerField(default=0)
    last_watch_date = models.DateField(null=True, default=None)  # Count in days


class KeywordCount(models.Model):
    keyword = models.CharField(primary_key=True, null=False, max_length=KEYWORD_MAX_LENGTH)
    count = models.PositiveIntegerField(default=0)


class KeywordVideoId(models.Model):
    keyword = models.CharField(null=False, max_length=KEYWORD_MAX_LENGTH)
    video_id = models.PositiveIntegerField(primary_key=True)
