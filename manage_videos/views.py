import math
import os
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import QueryDict

from homesite.settings import config_dict
from video.models import Video, KeywordCount, KeywordVideoId

RECORDS_PER_PAGE = 20

# Create your views here.
@login_required
@permission_required('video.delete_video')
def index(request):
    return render(request, 'manage-videos.html')


@login_required
@permission_required('video.add_video')
def import_videos(request):
    return render(request, 'import-videos.html')


@permission_required('video.add_video, video.change_video')
def load_dir(request):
    dir = request.POST['dir']

    if len(dir) > 512:
        return HttpResponse('Dir too long', status=400)

    upper_idx = dir.find('..')

    if upper_idx != -1:
        # Check if it contains '..' traps. For a sub path combined can be '/home/xxx/../../usr/local'
        if upper_idx != (len(dir) - 2):
            return HttpResponse('Bad directory: {0}'.format(dir), status=400)

        match = re.match(r'(.*)/[^/]+/\.\.$', dir)
        dir = ""
        if match is not None:
            dir = match.groups()[0]

    root = config_dict.get('load_dir_root', os.getenv('HOME'))
    path = os.path.join(root, dir)

    if not path.startswith(root):
        return HttpResponse('Requested dir not allowed', status=403)

    if not os.path.isdir(path):
        return HttpResponse('No such directory: {0}'.format(path), status=404)

    dir_list = []
    file_list = []
    if path != root:
        dir_list.append(['..', True])
    for fn in os.listdir(path):
        if fn.startswith('.'):
            continue

        entry = os.path.join(path, fn)

        if os.path.isdir(entry):
            dir_list.append([fn, True])
        else:
            file_list.append([fn, False])
    entry_list = dir_list + file_list

    headers = ['Path', 'Type']
    current_dir = path[len(root):]
    return JsonResponse({'headers': headers, 'data': entry_list, 'current_dir': current_dir})


@permission_required('video.change_video')
def db(request, table):
    if request.method == 'GET':
        page = int(request.GET['pg'])

        table_headers = []
        data = []
        page_num = 1
        if table == 'video':
            rating_header = 'rating[options(' + '|'.join([v for k, v in Video.RATING_CHOICES]) + ')]'
            table_headers = ['video_id', 'title[text]', 'duration',
                             'like_count[number]', 'dislike_count[number]',
                             'path',
                             rating_header]
            page_start = page * RECORDS_PER_PAGE
            page_end = (page + 1) * RECORDS_PER_PAGE
            page_num = math.ceil(Video.objects.all().count() * 1.0 / RECORDS_PER_PAGE)
            videos = Video.objects.all()[page_start: page_end]
            for v in videos:
                data.append([v.video_id, v.title, v.duration, v.like_count, v.dislike_count, v.path, v.rating])
        elif table == 'keywords':
            table_headers = ['keyword', 'count']
            page_start = page * RECORDS_PER_PAGE
            page_end = (page + 1) * RECORDS_PER_PAGE
            page_num = math.ceil(KeywordCount.objects.all().count() * 1.0 / RECORDS_PER_PAGE)
            keywords = KeywordCount.objects.all()[page_start: page_end]
            for k in keywords:
                data.append([k.keyword, k.count])

        return JsonResponse({'headers': table_headers, 'data':data, 'page-num': page_num})
    elif request.method == 'PUT':
        put = QueryDict(request.body)
        key = put.get('key')
        field = put.get('field')
        field_value = put.get('field-value')
        record = None
        if table == 'video':
            record = Video.objects.get(video_id=key)
        elif table == 'keywords':
            record = KeywordCount.objects.get(keyword=key)
        record.__setattr__(field, field_value)
        record.save()

        return HttpResponse('', status=200)
    elif request.method == 'DELETE':
        delete = QueryDict(request.body)
        keys = delete.get('keys')
        keys = keys.split(',')
        field = ''
        if table == 'video':
            field = 'video_id'
        elif table == 'keywords':
            field = 'keyword'
        condition = Q()
        for key in keys:
            condition.add((field, key), 'OR')
        if table == 'video':
            Video.objects.filter(condition).delete()
        elif table == 'keywords':
            KeywordCount.objects.filter(condition).delete()
            KeywordVideoId.objects.filter(condition).delete()
        return HttpResponse('Record removed', status=204)