# coding=utf8
# encoding: utf-8

import os
import platform
import re
import signal
import sys
import traceback
from subprocess import Popen, PIPE
from threading import Thread, current_thread

from Queue import Queue

from util.log import get_logger, log
from video.models import Video, KeywordVideoId
from django.db.models import Max
from collect_video import G_GEN_IMAGE

MAX_THREAD_NUM = 4
THREAD_STOP_FLAGS = []

THUMB_DIR = './static/thumb'
THUMB_SIZE = '180x135'
COVER_DIR = './static/cover'
FLIP_DIR = './static/flip'

FLIP_NUM = 10

task_queue = Queue(maxsize=2000)


def register_int_signal_handler():
    def stop_thread_handler(signum, frame):
        log.info("Received signal {0}. Will stop all task threads".format(signum))
        for _ in range(len(THREAD_STOP_FLAGS)):
            THREAD_STOP_FLAGS[_] = True

    if platform.platform().startswith('Windows'):
        signal.signal(signal.CTRL_C_EVENT, stop_thread_handler)
    else:
        signal.signal(signal.SIGINT, stop_thread_handler)


def next_video_id(current, path):
    existing = Video.objects.filter(path=path)
    if existing:
        return existing[0].video_id, current
    current += 1
    return current, current

def create_task_list(path_list):
    """
    Walks path recursively, and create a task list
    :param path_list: a list of (path, rating)
    :return: a list of ImportTask objects
    """
    current_video_id = Video.objects.all().aggregate(Max('video_id'))['video_id__max']
    if not current_video_id:
        current_video_id = 0

    task_list = []
    for (path, rating) in path_list:
        base_path = os.path.split(path)[0]
        if os.path.isfile(path):
            file_name = os.path.basename(path)
            if is_valid_video_file(path, file_name):
                video_id, current_video_id = next_video_id(current_video_id, path)
                task_list.append(ImportTask(video_id, base_path, path, rating))
            continue
        for (root, dirs, files) in os.walk(path):
            for file_name in files:
                try:
                    file_path = os.path.join(root, file_name)
                    if os.path.isdir(file_path):
                        continue
                    if is_valid_video_file(file_path, file_name):
                        video_id, current_video_id = next_video_id(current_video_id, file_path)
                        task_list.append(ImportTask(video_id, base_path, file_path, rating))
                except:
                    log.error('#Error while proceeding: {0}'.format(file_name))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return task_list


def start_tasks(task_list):
    global task_queue
    for task in task_list:
        task_queue.put(task)

    if not THREAD_STOP_FLAGS:
        for _ in range(MAX_THREAD_NUM):
            THREAD_STOP_FLAGS.append(True)

    if not os.path.isdir(COVER_DIR):
        os.mkdir(COVER_DIR)
    if not os.path.isdir(THUMB_DIR):
        os.mkdir(THUMB_DIR)
    if not os.path.isdir(FLIP_DIR):
        os.mkdir(FLIP_DIR)
    for _ in range(MAX_THREAD_NUM):
        if THREAD_STOP_FLAGS[_]:
            t = Thread(target=import_worker, kwargs={'thread_index': _})
            t.name = str(_)
            t.daemon = False
            t.start()

    task_queue.join()


def add_keywords_to_db(task_list):
    blacklist = load_keyword_blacklist_from_file()
    for task in task_list:
        base_path = task.base_path
        file_path = task.file_path
        video_id = task.video_id

        keywords = get_keywords(base_path, file_path, blacklist)

        log.info('#Keywords:'.format(keywords))
        for key in keywords:
            try:
                if KeywordVideoId.objects.filter(keyword=key, video_id=video_id):
                    log.info("Existing keyword {0} for {1}".format(key, video_id))
                    continue
                keyword_record = KeywordVideoId()
                keyword_record.keyword = key
                keyword_record.video = Video.objects.get(video_id=video_id)
                keyword_record.save()
                log.info('#Added keyword:{0} for video_id: {1}'.format(key, video_id))
            except Exception as e:
                log.error("Error while adding keyword {0} to video {1}: {2}".format(key, video_id, e))


class ImportTask(object):
    def __init__(self, video_id, base_path, path, rating=Video.P):
        """
        Create an import task object.
        :param video_id: a pre-allocated video_id in number, so we don't need to lock db in multiple thread.
        :param base_path: path prefix that will be ignored when creating keywords from path.
        :param path: path of the file
        :param rating: rating of the video, highest by default.
        """
        self.video_id = video_id
        self.base_path = base_path
        self.file_path = path
        self.rating = rating


def import_worker(thread_index):
    """
    Thread worker that deals with tasks.
    :return:
    """
    THREAD_STOP_FLAGS[thread_index] = False
    while not (THREAD_STOP_FLAGS[thread_index] or task_queue.empty()):
        task = task_queue.get()
        do_import_video_task(task)
        task_queue.task_done()
    THREAD_STOP_FLAGS[thread_index] = True


def do_import_video_task(task):
    video_id = task.video_id
    file_path = task.file_path
    rating = task.rating
    file_name = os.path.basename(file_path)[:-4]

    tlog = get_logger(current_thread().name)
    videos = Video.objects.filter(path=file_path)
    if videos:
        tlog.info("Existing video: {0}".format(task.file_path))
        return
    video = Video()
    video.video_id = video_id
    video.rating = rating

    thumb_path = get_thumb_path(video.video_id)
    cover_path = get_cover_path(video.video_id)
    if not gen_cover(task.file_path, cover_path):
        tlog.error("Failed to gen cover for {0}".format(file_path))
        return

    success, duration = gen_thumb(file_path, thumb_path)
    if success:
        if not gen_flips(file_path, video.video_id, duration, FLIP_DIR, FLIP_NUM):
            tlog.error("Failed to gen flips for {0}".format(file_path))
    else:
        tlog.error("Failed to gen thumb for {0}".format(file_path))

    video.title = file_name
    video.path = file_path
    video.duration = duration
    video.save()
    tlog.info('#Video: {0} [{1}] {2}'.format(video.title, video.duration, video.path))


def is_valid_video_file(file_path, file_name):
    # skip hidden files (possibly not valid video files)
    if file_name.startswith('.') or (not file_name.endswith('.mp4')):
        return False
    if os.path.getsize(file_path) == 0:
        log.info('Remove invalid video file: {0}'.format(file_path))
        os.remove(file_path)
        return False
    return True


def load_keyword_blacklist_from_file():
    blacklist = set()
    keyword_file = 'keywords.blacklist'
    try:
        with open(keyword_file, 'r') as kfp:
            for line in kfp:
                line = line.strip('\n')
                if line:
                    blacklist.add(line)
        log.info("Keywords blacklist: {0}".format(blacklist))
    except Exception as e:
        log.error("Error while processing {0}:{1}".format(keyword_file, e))
    return blacklist


def get_keywords(prefix, file_path, blacklist):
    """
    Get keywords from file path
    :param prefix: Prefix of the dir path, so we can ignore them
    :param file_path: full path of the video file
    :param blacklist: A set of words/symbols that should be ignored
    :return: a list of keywords
    """
    file_path = str(file_path).replace(prefix, '')  # remove base_dir from file_path
    file_path = os.path.splitext(file_path)[0]  # Only keep the part without extension
    file_path = str(file_path).lower()
    for bad_keyword in blacklist:
        file_path = file_path.replace(bad_keyword, ' ')
    file_path = re.sub(r'\s+', ' ', file_path)  # Replace multiple spaces to single one
    keywords = file_path.split(' ')
    keywords = [k for k in keywords if k]

    return keywords



class KeywordDictDataObj(object):
    def __init__(self):
        self.count = 0
        self.files = set()


def get_thumb_path(fn):
    return './static/thumb/' + str(fn) + '.png'


def get_cover_path(fn):
    return './static/cover/' + str(fn) + '.png'


def gen_thumb(video_path, thumb_path):
    """
    Generate thumb image for the given video, and grabs duration from output
    :return: (success, duration)
    """
    if os.path.isfile(thumb_path):
        os.remove(thumb_path)

    global THUMB_SIZE
    cmd = ['ffmpeg', '-itsoffset', '-5', '-i', video_path, '-vframes', '1', '-f', 'apng', '-s', THUMB_SIZE, thumb_path]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output = p.communicate()[1]

    duration = search_duration_from_text(output)
    if not duration:
        tlog = get_logger(current_thread().name)
        tlog.error("Failed to find duration for {0}".format(video_path))
        duration = 0

    return p.returncode == 0, duration


def gen_flips(video_path, video_id, duration, flip_path, flip_num):
    """
    Generate flips for the given video
    :param video_path: path of the video
    :param video_id: id of the file
    :param duration: duration of video in seconds
    :param flip_path: path dir to put the flips
    :param flip_num: number of flips to generate
    :return: True on success, False otherwise
    """
    if not G_GEN_IMAGE:
        return True

    duration = float(duration)
    flip_num = float(flip_num)
    interval = duration / flip_num
    if interval <= 0.0:
        tlog = get_logger(current_thread().name)
        tlog.error("Cannot generate flips. Duration: {0} FlipNum:{1}".format(duration, flip_num))
        return False
    fps = 'fps=1/' + str(interval)
    global THUMB_SIZE
    flip_path = os.path.join(flip_path, str(video_id))
    for _ in range(FLIP_NUM+3):
        flip_file = "{0}-{1}.png".format(flip_path, _)
        if os.path.isfile(flip_file):
            os.remove(flip_file)
    flip_path_template = flip_path + '-%d.png'
    cmd = ['ffmpeg', '-i', video_path, '-vf', fps, '-s', THUMB_SIZE, flip_path_template]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate()

    return p.returncode == 0


def gen_cover(video_path, cover_path):
    if not G_GEN_IMAGE:
        return True
    if os.path.isfile(cover_path):
        os.remove(cover_path)

    cmd = ['ffmpeg', '-itsoffset', '-1', '-i', video_path, '-vframes', '1', '-f', 'apng', cover_path]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate()

    return p.returncode == 0


# Convert video to mp4
def convert_video_to_mp4(video_path, dest_path):
    tlog = get_logger(current_thread().name)
    if os.path.isfile(dest_path):
        tlog.info('#Already converted, skip: {0}'.format(dest_path))
        return True
    tlog.info('#Converting: {0} => {1}\n', video_path, dest_path)

    cmd = ['ffmpeg', '-i', video_path, '-vcodec', 'h264', '-acodec', 'aac', dest_path]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate()

    return p.returncode == 0


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
