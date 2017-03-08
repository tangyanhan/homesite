from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Video
from models import KeywordCount
from models import KeywordPathHash
from models import KEYWORD_MAX_LENGTH
import json
import os
import math

import datetime

RECENT_DAYS = 7

RECENT_CACHE = {
	'date':'',
	'records':[]
}

SEARCH_CACHE = {
	# keyword : [result list] TODO: add date
}

RESULT_NUM_PER_PAGE = 10

def index(request):
	return render(request, 'video-index.html')

# Create your views here.
def loadRecentRecords():
	today = datetime.date.today()

	global RECENT_CACHE
	if len(RECENT_CACHE) > 0:
		delta = today - RECENT_CACHE['date']
		# If recent is loaded less than 1 day ago, ignore it
		if delta.days < 1:
			return RECENT_CACHE['records']

	global RECENT_DAYS
	min_date = today - datetime.timedelta(days=RECENT_DAYS)
	recent_records = Video.objects.filter(import_date__range=[min_date.strftime('%Y-%m-%d') , today.strftime('%Y-%m-%d')])


	RECENT_CACHE['records'] = []

	list = RECENT_CACHE['records']
	for video in recent_records:
		dict = dictForVideo(video)
		if dict is None:
			continue

		list.append(dict)
	return list

def dictForVideo(video):
	if os.path.isfile(video.path):
		return {'id':video.path_hash, 'title':video.title}

	return None

def play(request,digest):
	return render(request,'video-player.html', {'video':digest, 'thumb':'thumb/'+ digest +'.png'})


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
			results = loadRecentRecords()
		else:
			results = loadSearchResultsWithKeyword(keyword)

		global RESULT_NUM_PER_PAGE
		pageNum = math.ceil(len(results) / RESULT_NUM_PER_PAGE) # TODO: check if python has a same old ceil problem

		if idx >= pageNum:
			return render(request,'404.html')

		beginIdx = idx * RESULT_NUM_PER_PAGE
		endIdx = beginIdx + RESULT_NUM_PER_PAGE
		if endIdx > len(results):
			endIdx = len(results)
		pageRecords = results[beginIdx:endIdx]

		jsonData = json.dumps({'pageNum':pageNum, 'results':pageRecords})
		return jsonData
	except:
		return render(request, '500.html')

def loadSearchResultsWithKeyword(keyword):
	try:
		# Retrieve from cache first
		if keyword in SEARCH_CACHE:
			return SEARCH_CACHE[keyword]

		# No results in cache, load from database
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
				dict = dictForVideo(videos[0])
				results.append(dict)
		return results
	except:
		return []

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