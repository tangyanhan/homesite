from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Video
from models import KeywordCount
from models import KeywordPathHash
from models import KEYWORD_MAX_LENGTH
import json

import datetime

RECENT_DAYS = 7

# Create your views here.
def index(request):
	today = datetime.date.today()

	global RECENT_DAYS
	min_date = today - datetime.timedelta(days=RECENT_DAYS)
	recent_records = Video.objects.filter(import_date__range=[min_date.strftime('%Y-%m-%d') , today.strftime('%Y-%m-%d')])


	new_added_videos = []
	if recent_records is not None:
		for video in recent_records:
			thumb = 'thumb/' + video.path_hash + '.png'
			new_added_videos.append((video.path_hash,thumb,video.title))

	return render(request, 'video-index.html', {'new_added_videos':new_added_videos})

def play(request,digest):

	return render(request,'video-player.html', {'video':digest, 'thumb':'thumb/'+ digest +'.png'})

def search(request):
	try:

		keyword = request.GET['keyword']

		keys = keyword.split(' ')

		resultSet = set()
		records = KeywordPathHash.objects.filter(keyword__contains=keys[0])
		titleRecords = Video.objects.filter(title__contains=keys[0])
		for key in keys[1:]:
			records = records.filter(keyword__contains=key)
			titleRecords = titleRecords.filter(title__contains=key)

		for record in records:
			resultSet.add(record.path_hash)

		for record in titleRecords:
			resultSet.add(record.path_hash)

		results = []
		for path_hash in resultSet:
			videos = Video.objects.filter(path_hash=path_hash)
			if len(videos) > 0:
				thumb = 'thumb/' + path_hash + '.png'
				results.append((path_hash, thumb, videos[0].title))

		return render(request, 'video-index.html', {'search_results':results})
	except:
		return render(request,'500.html')

def keyword_suggest(request):
	keyword = request.POST['keyword']

	if len(keyword) > KEYWORD_MAX_LENGTH:
		return HttpResponse('')

	availableKeywords = KeywordCount.objects.filter(keyword__contains=keyword)

	if len(availableKeywords) > 0:
		sugList = []
		for record in availableKeywords:
			sugList.append(record.keyword)

		return HttpResponse(json.dumps(sugList))

	return HttpResponse('')

def video_import(request):
	path = request.POST['path']

	return HttpResponse('TODO://implement video import')

def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response