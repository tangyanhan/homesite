from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from homesite.settings import config_dict
from video.models import Video, KeywordCount

import json
import os
import re

RECORDS_PER_PAGE = 50

# Create your views here.
def index(request):
    return render(request, 'manage-videos.html')


def import_videos(request):
    return render(request, 'import-videos.html')


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


def db(request):
    table = request.POST['table']
    page = int(request.POST['pg'])

    table_headers = []
    data = []
    if table == 'video':
        table_headers = ['ID', 'Title', 'Duration', 'Like', 'Dislike', 'Path']
        page_start = page * RECORDS_PER_PAGE
        page_end = (page + 1) * RECORDS_PER_PAGE
        videos = Video.objects.all()[page_start: page_end]
        for v in videos:
            data.append([v.video_id, v.title, v.duration, v.like_count, v.dislike_count, v.path])
    elif table == 'keywords':
        table_headers = ['Keyword', 'Count']
        page_start = page * RECORDS_PER_PAGE
        page_end = (page + 1) * RECORDS_PER_PAGE
        keywords = KeywordCount.objects.all()[page_start: page_end]
        for k in keywords:
            data.append([k.keyword, k.count])

    return JsonResponse({'headers': table_headers, 'data':data})

