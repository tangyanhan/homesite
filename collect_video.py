#!/usr/bin/env python
# coding=utf-8

import sys
import os
from subprocess import Popen, PIPE
import re
import traceback

# TODO: we should make it in a public library like 'supported format'
supported_video_formats = ['mp4', 'mov', 'wmv', 'rmvb', 'rm', 'avi']

THUMB_DIR = './static/thumb'
THUMB_SIZE = '180x135'
COVER_DIR = './static/cover'

g_change_db = True

FILE_NAME_REG = None

VIDEO_ID = 0


class KeywordDictDataObj(object):
    def __init__(self):
        self.count = 0
        self.files = set()


def get_filename_tuple(file_path):
    global FILE_NAME_REG
    if FILE_NAME_REG is None:
        formats = ''
        first = True
        global supported_video_formats
        for f in supported_video_formats:
            if first:
                first = False
            else:
                formats += r'|'
            formats += f

        FILE_NAME_REG = re.compile(r'(.*)/([^/]+)\.(' + formats + r')$', re.UNICODE | re.IGNORECASE)

    match = FILE_NAME_REG.match(file_path)

    if match is not None:
        return True, match.groups()

    return False, None, None, None


def get_thumb_path(fn):
    if not os.path.isdir(THUMB_DIR):
        os.mkdir(THUMB_DIR)

    return './static/thumb/' + str(fn) + '.png'


def get_cover_path(fn):
    if not os.path.isdir(COVER_DIR):
        os.mkdir(COVER_DIR)

    return './static/cover/' + str(fn) + '.png'


# TODO: we should use an advanced method to analyze them
# @return: a list of keywords concaternated together
def get_keywords(base_dir, file_path):
    file_path = str(file_path).replace(base_dir, '')  # remove base_dir from file_path
    file_path = os.path.splitext(file_path)[0]  # Only keep the part without extension
    file_path = str(file_path).lower()
    file_path = re.sub(r'[/.#]', ' ', file_path)  # Replace meaningless symbols to space
    file_path = re.sub(r'\s+', ' ', file_path)  # Replace multiple spaces to single one
    keywords = file_path.split(' ')

    return keywords


# Build dict from database
def build_keyword_dict():
    d = {}
    keywords = KeywordCount.objects.all()

    for key in keywords:
        data = KeywordDictDataObj()
        data.count = key.count
        d[key.keyword] = data

    del keywords

    key_vid_list = KeywordVideoId.objects.all()
    for kv in key_vid_list:
        if kv.keyword in d:
            data = d[kv.keyword]
            data.files.add(kv.video_id)
        else:
            log.error('#Keyword not found: {0}'.format(kv))
    return d


def save_dict_to_db(d):
    # Save dict to database
    for key in d:
        data = d[key]
        log.info('#{0}# Count={1}'.format(key, data.count))
        for vid_id in data.files:
            log.info('\tvideo_id:{0}'.format(vid_id))
        if data.count > 0:
            kcs = KeywordCount.objects.filter(keyword=key)
            if len(kcs) > 0:
                kc = kcs[0]
            else:
                kc = KeywordCount()
            kc.keyword = key
            kc.count = data.count

            if g_change_db:
                kc.save()

            for vid_id in data.files:
                files = KeywordVideoId.objects.filter(keyword=key, video_id=vid_id)
                if not files:
                    kph = KeywordVideoId()
                    kph.keyword = key
                    kph.video_id = vid_id

                    if g_change_db:
                        kph.save()


def next_video_id():
    global VIDEO_ID
    VIDEO_ID += 1
    return VIDEO_ID


def visit_dir(base_dir):
    base_dir = os.path.abspath(base_dir)
    dict = build_keyword_dict()

    max_video_id = Video.objects.all().aggregate(Max('video_id'))['video_id__max']

    if max_video_id is not None:
        global VIDEO_ID
        VIDEO_ID = max_video_id

    for (root, dirs, files) in os.walk(sys.argv[1]):
        for fn in files:
            try:
                file_path = os.path.join(root, fn)

                if os.path.isdir(file_path):
                    continue

                success, file_dir, file_name, ext = get_filename_tuple(file_path)

                if not success:
                    continue

                # skip hidden files (possibly not valid video files)
                if file_name.startswith('.'):
                    continue

                need_convert = False
                if ext.lower() != 'mp4':
                    need_convert = True
                    # Disable video convert for the time being, we should convert them in idle time
                    if True:
                        mp4_path = os.path.join(file_dir, file_name)
                        mp4_path += '.mp4'
                        if not convert_video_to_mp4(file, mp4_path):
                            log.error('#Failed to convert file to mp4: {0}'.format(file))
                            continue
                        else:
                            need_convert = False
                            file = mp4_path
                            ext = 'mp4'
                elif os.path.getsize(file) == 0:
                    log.info('Remove invalid video file: {0}'.format(file))
                    os.remove(file)
                    continue

                video_id = next_video_id()

                videos = Video.objects.filter(video_id=video_id)

                if videos:
                    video = videos[0]
                else:
                    video = Video()
                    video.video_id = video_id
                    video.need_convert = need_convert

                thumb_path = get_thumb_path(video_id)

                cover_path = get_cover_path(video_id)
                output = gen_cover(file, cover_path)
                output = gen_thumb(file, thumb_path)

                if output is None:
                    continue

                duration = search_duration_from_text(output)
                del output

                if not duration:
                    log.error('#Failed to get duration from {0}'.format(file))
                    duration = 0

                keywords = get_keywords(base_dir, file)

                log.info('#Keywords:'.format(keywords))
                for key in keywords:
                    if len(key) == 0:
                        continue
                    else:
                        log.info('#Added keyword:'.format(key))

                    data = None
                    if key in dict:
                        data = dict[key]
                    else:
                        data = KeywordDictDataObj()
                        dict[key] = data

                    if video_id not in data.files:
                        data.count = data.count + 1
                        data.files.add(video_id)
                video.title = file_name
                video.path = file
                video.duration = duration
                if g_change_db:
                    video.save()
                log.info('#Video: {0} [{1}] {2}'.format(video.title, video.duration, video.path))

            except:
                log.error('#Error while proceeding: {0}'.format(fn))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    save_dict_to_db(dict)


# Generate thumbnail of given video. Delete thumb_path if thumb_path already exists
# @return: command output of ffmpeg
def gen_thumb(video_path, thumb_path):
    if os.path.isfile(thumb_path):
        os.remove(thumb_path)

    global THUMB_SIZE
    cmd = ['ffmpeg', '-itsoffset', '-5', '-i', video_path, '-vframes', '1', '-f', 'apng', '-s', THUMB_SIZE, thumb_path]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output = p.communicate(input="y\n")[1]  # TODO: need a solution to answer questions

    return output


def gen_cover(video_path, cover_path):
    if os.path.isfile(cover_path):
        os.remove(cover_path)

    cmd = ['ffmpeg', '-itsoffset', '-1', '-i', video_path, '-vframes', '1', '-f', 'apng', cover_path]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output = p.communicate()

    return output


# Convert video to mp4
def convert_video_to_mp4(video_path, dest_path):
    if os.path.isfile(dest_path):
        log.info('#Already converted, skip: {0}'.format(dest_path))
        return True
    log.info('#Converting: {0} => {1}\n', video_path, dest_path)

    cmd = ['ffmpeg', '-i', video_path, '-vcodec', 'h264', '-acodec', 'aac', dest_path]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    p.communicate()

    # Remove old if succeeded
    if os.path.isfile(dest_path) and os.path.getsize(dest_path) > 0:
        os.remove(video_path)
        return True
    os.remove(dest_path)

    return False


# Search the duration from given text
def search_duration_from_text(text):
    # Match pattern like Duration: 00:24:14.91, s
    regExp = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2})')
    result = regExp.search(text, re.M | re.U)

    if result is not None:
        (hour, min, sec) = result.groups()
        duration = int(hour) * 3600 + int(min) * 60 + int(sec)
        return duration
    return None


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

    from django.db.models import Max

    from util.log import log
    from video.models import Video
    from video.models import KeywordCount
    from video.models import KeywordVideoId

    search_dir = sys.argv[1]

    if len(sys.argv) > 2:
        if sys.argv[2] == 'nosave':
            g_change_db = False
    log.info('###### Begin searching videos in ', search_dir)

    visit_dir(search_dir)
