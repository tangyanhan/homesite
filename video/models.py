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
    # Similar to American movie rating system.
    # Audience permission>rating is allowed to watch the movie
    G = 'G'
    PG = 'PG'
    PG13 = 'PG13'
    R = 'R'
    NC17 = 'NC17'
    RATING_CHOICES = (
        (G, 'For general audiences'),
        (PG, 'Parental guidance'),
        (PG13, 'Parents Strongly Cautioned'),
        (R, 'Restricted'),
        (NC17, 'NO ONE AND UNDER 17 ADMITTED')
    )
    rating = models.CharField(max_length=4, choices=RATING_CHOICES, default=R)


class KeywordCount(models.Model):
    keyword = models.CharField(primary_key=True, null=False, max_length=KEYWORD_MAX_LENGTH)
    count = models.PositiveIntegerField(default=0)


class KeywordVideoId(models.Model):
    keyword = models.CharField(null=False, max_length=KEYWORD_MAX_LENGTH)
    video_id = models.PositiveIntegerField(primary_key=True)
