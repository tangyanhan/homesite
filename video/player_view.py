import sys
import re
import traceback

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from models import Video
from models import KeywordVideoId
from views import load_recent_records
from views import dict_for_video

MAX_RECOMMEND_NUM = 10


@login_required
def play(request, digest):
    return render(request, 'video-player.html', {'video': digest, 'thumb': 'thumb/' + digest + '.png'})


def rate(request):
    try:
        if not request.user.is_authenticated:
            pass

        video_id = request.POST['id']
        option = int(request.POST['op'])
        if option not in [1, -1]:
            return HttpResponse('', status=400)
        results = Video.objects.filter(video_id=video_id)

        if len(results) != 1:
            return HttpResponse('', status=404)

        video = results[0]
        if option == 1:
            video.like_count += 1
        elif option == -1:
            video.dislike_count += 1
        video.save()

        return JsonResponse({'like': video.like_count, 'dislike': video.dislike_count})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        return HttpResponse('', status=500)


# Recommend videos in player page. So users can play at their own interest
def recommend(request):
    try:
        video_id = int(request.POST['id'])
        video = Video.objects.get(video_id=video_id)

        video_list = []
        check_set = set()
        check_set.add(video_id)
        # First, look for videos in the same directory

        file_name_reg = re.compile(r'(.*)/[^/]+$', re.UNICODE | re.IGNORECASE)
        dir = file_name_reg.search(video.path).groups()[0]

        # BUG BUG: Bug here
        if len(dir) > 0:
            videos_in_same_dir = Video.objects.filter(path__contains=dir)
            for vid in videos_in_same_dir:
                if vid.video_id not in check_set:
                    check_set.add(vid.video_id)
                    video_list.append(dict_for_video(vid))

        if len(video_list) < MAX_RECOMMEND_NUM:
            # Second, look for videos with similar keywords
            keywords = KeywordVideoId.objects.filter(video_id=video_id)
            for record in keywords:
                keyword = record.keyword
                videos = KeywordVideoId.objects.filter(keyword=keyword)
                for vid in videos:
                    if vid.video_id not in check_set:
                        check_set.add(vid.video_id)
                        video = Video.objects.get(video_id=video_id)
                        video_list.append(dict_for_video(video))
            # Third, look for recently added
            if len(video_list) < MAX_RECOMMEND_NUM:
                recent_records = load_recent_records()
                for record in recent_records:
                    if record['id'] not in check_set:
                        check_set.add(record['id'])
                        video_list.append(record)
        # Trim if necessary
        if len(video_list) > MAX_RECOMMEND_NUM:
            video_list = video_list[0:MAX_RECOMMEND_NUM]

        return JsonResponse({'videos': video_list})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        return HttpResponse('', status=500)
