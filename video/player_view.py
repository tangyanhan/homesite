import re
import sys
import traceback

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from custom_user.models import CustomUser
from models import KeywordVideoId
from models import Video
from views import dict_for_video

MAX_RECOMMEND_NUM = 10


def play(request, video_id):
    rating = Video.G
    if isinstance(request.user, CustomUser):
        rating = request.user.rating
    video = Video.objects.filter(video_id=video_id)
    if rating < video[0].rating:
        return HttpResponse('You are not permitted to access this content', status=403)
    return render(request, 'video-player.html', {'video': video_id, 'thumb': 'thumb/' + video_id + '.png'})


def rate(request):
    try:
        if not request.user.is_authenticated:
            pass

        video_id = request.POST['id']
        option = int(request.POST['op'])
        if option not in [1, 0, -1]:
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
        rating = Video.G
        if isinstance(request.user, CustomUser):
            rating = request.user.rating

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
                records = Video.objects.filter(rating__lte=rating).order_by('-import_date')
                recent_records = [dict_for_video(video) for video in records]
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
