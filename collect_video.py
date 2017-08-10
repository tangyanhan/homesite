#!/usr/bin/env python
# coding=utf8
# encoding: utf-8

import os
import re
import sys

THUMB_DIR = './static/thumb'
THUMB_SIZE = '180x135'
COVER_DIR = './static/cover'
FLIP_DIR = './static/flip'

FLIP_NUM = 16

G_GEN_IMAGE = True


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.stderr.write('''
        Arguments: path_to_search [nosave]
        When nosave is given, no changes will be written to database
''')
        exit(0)

    # Import Django modules
    os.environ.update({"DJANGO_SETTINGS_MODULE": "homesite.settings"})
    import django

    django.setup()

    from util.log import log
    from video.models import Video
    from manage_videos.import_videos import create_task_list, start_tasks, add_keywords_to_db, register_int_signal_handler

    path = sys.argv[1]

    rating = Video.P
    if len(sys.argv) > 2:
        for arg in sys.argv:
            if arg == 'noimage':
                G_GEN_IMAGE = False
            elif arg.startswith('rating='):
                rating_arg = arg[len('rating='):]
                rating = Video.RATING_MAP.get(rating_arg, None)

                if rating is None:
                    log.error("Invalid rating option: {0}. Valid options are {1}".
                              format(rating_arg, [k for k, v in Video.RATING_MAP.items()]))
                    sys.exit(1)

    rating_detail = [v for k, v in Video.RATING_CHOICES if k == rating]
    log.info('# Creating tasks for path: {0}  Movie rating: {0} {1}'.format(path, rating, rating_detail))
    task_list = create_task_list([(path, rating)])
    log.info("# {0} tasks to be done ...".format(len(task_list)))
    register_int_signal_handler()
    start_tasks(task_list)
    log.info("# Adding keywords ...")
    add_keywords_to_db(task_list)
    log.info("# Job Complete !!!")
