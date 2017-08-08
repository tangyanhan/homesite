import json
import math
import os
import re
import sys
import traceback

from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from custom_user.models import CustomUser
from models import KEYWORD_MAX_LENGTH
from models import KeywordCount
from models import KeywordVideoId
from models import Video
from util import log

RECENT_DAYS = 7

MAX_KEYWORD_LEN = 50

RESULT_NUM_PER_PAGE = 40  # Make it float to avoid bad results from ceil when calculating total page num


def dict_for_video(video):
    if os.path.isfile(video.path):
        return {'id': video.video_id, 'title': video.title, 'duration': video.duration}

    return None


def videos(request):
    try:
        keyword = None
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
        idx = 0
        if 'idx' in request.GET:
            idx = int(request.GET['idx'])
        rating = Video.G
        if isinstance(request.user, CustomUser):
            rating = request.user.rating

        if not keyword:
            records = Video.objects.filter(rating__lte=rating).order_by('-import_date')
            results = [dict_for_video(video) for video in records]
            keyword = ''
        else:
            # Deal with keyword
            keys = convert_keyword(keyword)

            keyword = ' '.join(keys)
            results = load_search_result_with_keyword(keys, rating)

        if not results:
            return render(request, 'video-index.html', {
                'keyword': keyword,
                'idx': idx,
                'page_num': 0,
                'results': json.dumps([])}
                          )

        page_num = math.ceil(1.0 * len(results) / RESULT_NUM_PER_PAGE)

        if idx >= page_num:
            raise Http404

        begin_idx = idx * RESULT_NUM_PER_PAGE
        end_idx = begin_idx + RESULT_NUM_PER_PAGE
        if end_idx > len(results):
            end_idx = len(results)

        results = results[begin_idx:end_idx]

        return render(request, 'video-index.html',
                      {
                        'keyword': keyword,
                        'idx': idx,
                        'page_num': page_num,
                        'results': json.dumps(results)
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


def load_search_result_with_keyword(keys, rating):
    try:
        condition = Q()
        for key in keys:
            condition.add(('keyword__icontains', key), 'AND')
        condition.add(('rating__lte', rating), 'AND')
        records = KeywordVideoId.objects.select_related().filter(condition).distinct('video')

        results = [dict_for_video(item.video) for item in records]
        return results
    except Exception as e:
        log.error("Error searching result with keyword:{0} {1}".format(keys, e))
        return QuerySet()


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
