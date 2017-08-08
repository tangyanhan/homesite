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
    G = 0
    PG = 1
    PG13 = 2
    R = 3
    NC17 = 4
    P = 5
    RATING_MAP = {
        'G': 0,
        'PG': 1,
        'PG13': 2,
        'R': 3,
        'NC17': 4,
        'P': 5
    }
    RATING_CHOICES = (
        (G, 'G: For general audiences'),
        (PG, 'PG: Parental guidance'),
        (PG13, 'PG13: Parents Strongly Cautioned'),
        (R, 'R: Restricted'),
        (NC17, 'NC17: NO ONE AND UNDER 17 ADMITTED'),
        (P, 'Private: Videos for private access')
    )
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=P)


class KeywordCount(models.Model):
    keyword = models.CharField(primary_key=True, null=False, max_length=KEYWORD_MAX_LENGTH)
    count = models.PositiveIntegerField(default=0)


class KeywordVideoId(models.Model):
    keyword = models.CharField(null=False, max_length=KEYWORD_MAX_LENGTH)
    video = models.ForeignKey(Video)





