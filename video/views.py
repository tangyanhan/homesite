import datetime
import json
import math
import os
import re
import sys
import traceback

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from models import Video
from models import KeywordCount
from models import KeywordVideoId
from models import KEYWORD_MAX_LENGTH


RECENT_DAYS = 7

MAX_KEYWORD_LEN = 50

RESULT_NUM_PER_PAGE = 40.0  # Make it float to avoid bad results from ceil when calculating total page num

RECENT_CACHE = {
    'date': '',
    'records': []
}

SEARCH_CACHE = {
    # keyword : [result list] TODO: add date
}


# Create your views here.
def load_recent_records():
    today = datetime.date.today()

    global RECENT_CACHE
    if len(RECENT_CACHE['date']) > 0:
        delta = today - RECENT_CACHE['date']
        # If recent is loaded less than 1 day ago, ignore it
        if delta.days < 1:
            return RECENT_CACHE['records']

    global RECENT_DAYS
    min_date = today - datetime.timedelta(days=RECENT_DAYS)
    recent_records = Video.objects.filter(
        import_date__range=[min_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')])

    RECENT_CACHE['records'] = []

    l = RECENT_CACHE['records']
    for video in recent_records:
        dict = dict_for_video(video)
        if dict is None:
            continue

        l.append(dict)
    return l


def dict_for_video(video):
    if os.path.isfile(video.path):
        return {'id': video.video_id, 'title': video.title, 'duration': video.duration}

    return None


@login_required()
def videos(request):
    try:
        keyword = None
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
        idx = 0
        if 'idx' in request.GET:
            idx = int(request.GET['idx'])

        results = []
        if keyword is None or len(keyword) == 0:
            results = load_recent_records()
            keyword = ''
        else:
            # Deal with keyword
            keys = convert_keyword(keyword)

            keyword = ' '.join(keys)
            with_keyword = load_search_result_with_keyword(keys)
            results = with_keyword

        if not results:
            return render(request, 'video-index.html', {
                'keyword': keyword,
                'idx': idx,
                'page_num': 0,
                'results': json.dumps([])}
                          )

        global RESULT_NUM_PER_PAGE
        page_num = math.ceil(len(results) / RESULT_NUM_PER_PAGE)  # TODO: check if python has a same old ceil problem

        num = page_num
        if idx >= num:
            return render(request, '404.html')

        begin_idx = int(idx * RESULT_NUM_PER_PAGE)
        end_idx = int(begin_idx + RESULT_NUM_PER_PAGE)
        if end_idx > len(results):
            end_idx = len(results)

        page_records = results[begin_idx:end_idx]

        return render(request, 'video-index.html',
                      {
                        'keyword': keyword,
                        'idx': idx,
                        'page_num': page_num,
                        'results': json.dumps(page_records)
                      }
                      )
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        return render(request, '500.html')


# Deal with keywords, convert them to easier case
def convert_keyword(keyword):
    # Cut off if too long
    global MAX_KEYWORD_LEN
    if len(keyword) > MAX_KEYWORD_LEN:
        keyword = keyword[0:MAX_KEYWORD_LEN]

    keyword = keyword.lower()
    keyword = re.sub(r'[/.#$%^&*()-+=]', ' ', keyword)  # Replace meaningless symbols to space
    file_path = re.sub(r'\s+', ' ', keyword)  # Replace multiple spaces to single one

    keys = file_path.split(' ')

    return keys


def load_search_result_with_keyword(keys):
    try:
        # pdb.set_trace()
        result_set = set()
        for key in keys:
            period_set = set()
            if key in SEARCH_CACHE:
                period_set = SEARCH_CACHE[key]
            else:
                merged_records = KeywordVideoId.objects.filter(keyword__icontains=key)
                for record in merged_records:
                    period_set.add(record.video_id)

                if len(period_set) > 0:
                    SEARCH_CACHE[
                        key] = period_set  # TODO: cache stragety is too simple and may result to memory issue in future
            if result_set:
                result_set = result_set.intersection(period_set)
            else:
                result_set = period_set

        results = []
        for video_id in result_set:
            video = Video.objects.get(video_id=video_id)
            if video is not None:
                d = dict_for_video(video)
                results.append(d)
        return results
    except:
        return []


# Suggest keyword to client. This view don't need csrf
@csrf_exempt
def keyword_suggest(request):
    print '#Request type:', type(request)
    try:
        keyword = request.POST['keyword']
        if len(keyword) > KEYWORD_MAX_LENGTH:
            return HttpResponse('', status=400)

        # results ordered by count field in descending order
        available_keywords = KeywordCount.objects.filter(keyword__icontains=keyword).order_by('-count')

        if available_keywords:
            sug_list = []
            for record in available_keywords:
                sug_list.append(record.keyword)
            return JsonResponse({'keywords': sug_list})

        return HttpResponse('', status=404)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)
        return HttpResponse('', status=500)


def handler404(request, template_name='404.html'):
    return render_to_response(template_name)


def handler500(request, template_name='500.html'):
    return render_to_response(template_name)
