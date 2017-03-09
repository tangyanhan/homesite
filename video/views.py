from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Video
from models import KeywordCount
from models import KeywordPathHash
from models import KEYWORD_MAX_LENGTH
import json
import os
import sys
import math
import re
import traceback
import pdb
from itertools import chain

import datetime

RECENT_DAYS = 7

MAX_KEYWORD_LEN = 50

RESULT_NUM_PER_PAGE = 10.0 # Make it float to avoid bad results from ceil when calculating total page num

RECENT_CACHE = {
	'date':'',
	'records':[]
}

SEARCH_CACHE = {
	# keyword : [result list] TODO: add date
}

def index(request):
	return render(request, 'video-index.html', {'keyword':''})

# Create your views here.
def loadRecentRecords():
	today = datetime.date.today()

	global RECENT_CACHE
	if len(RECENT_CACHE['date']) > 0:
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
		return {'id':video.path_hash, 'title':video.title, 'duration':video.duration}

	return None

def play(request,digest):
	return render(request,'video-player.html', {'video':digest, 'thumb':'thumb/'+ digest +'.png'})


def videos(request):
	try:
		print '###Request'
		print request
		print '#######'
		keyword = None
		if 'keyword' in request.GET:
			keyword = request.GET['keyword']
		idx = 0
		if 'idx' in request.GET:
			idx = int(request.GET['idx'])

		print 'Keyword:',keyword,'idx:',idx

		results = []
		if keyword is None or len(keyword) == 0:
			results = loadRecentRecords()
			keyword = ''
		else:
			# Deal with keyword
			keys = convertKeyword(keyword)

			keyword = ' '.join(keys)
			results = loadSearchResultsWithKeyword(keys)

		global RESULT_NUM_PER_PAGE
		pageNum = math.ceil(len(results) / RESULT_NUM_PER_PAGE) # TODO: check if python has a same old ceil problem

		if idx >= pageNum:
			return render(request,'404.html')

		beginIdx = int(idx * RESULT_NUM_PER_PAGE)
		endIdx = int(beginIdx + RESULT_NUM_PER_PAGE)
		if endIdx > len(results):
			endIdx = len(results)
		pageRecords = results[beginIdx:endIdx]

		return render(request, 'video-index.html', {
			'keyword':keyword,
			'idx':idx,
			'pageNum':pageNum,
			'results': json.dumps(pageRecords)}
		              )

	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print "*** print_exception:"
		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
		return render(request, '500.html')

# Deal with keywords, convert them to easier case
def convertKeyword(keyword):
	# Cut off if too long
	global MAX_KEYWORD_LEN
	if len(keyword) > MAX_KEYWORD_LEN:
		keyword = keyword[0:MAX_KEYWORD_LEN]

	keyword = keyword.lower()
	keyword = re.sub(r'[/.#$%^&*()-+=]', ' ', keyword) #Replace meaningless symbols to space
	filePath = re.sub(r'\s+', ' ', keyword) #Replace multiple spaces to single one

	keys = filePath.split(' ')

	return keys

def loadSearchResultsWithKeyword(keys):
	try:
		# Retrieve from cache first
		if len(keys) == 1 and keys[0] in SEARCH_CACHE:
			return SEARCH_CACHE[keys[0]]

		resultSet = set()

		for key in keys:
			periodSet = set()
			if key in SEARCH_CACHE[ key ]:
				periodSet = SEARCH_CACHE[ key ]
			else:
				mergedRecords = chain(KeywordPathHash.objects.filter(keyword__contains=keys), Video.objects.filter(title__contains=keys))
				for record in mergedRecords:
					periodSet.add(record.path_hash)

				if len(periodSet) > 0:
					SEARCH_CACHE[ key ] = periodSet # TODO: cache stragety is too simple and may result to memory issue in future
			if len(resultSet) == 0:
				resultSet = periodSet
			else:
				resultSet = resultSet.intersection(periodSet)

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

		return JsonResponse(sugList)

	return JsonResponse([])

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