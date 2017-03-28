from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Video
from models import KeywordCount
from models import KeywordVideoId
from views import loadRecentRecords
from views import dictForVideo
import os
import sys
import pdb
import re
from django.contrib.auth.decorators import login_required

@login_required
def play(request,digest):
	return render(request,'video-player.html', {'video':digest, 'thumb':'thumb/'+ digest +'.png'})

#@csrf_exempt # TODO: should use auth
def rate(request):
	try:
		if not request.user.is_authenticated:
			pass

		video_id = request.POST['id']

		option = int(request.POST['op'])

		print 'video_id:',video_id,'option:',option

		results = Video.objects.filter(video_id=video_id)

		if len(results) != 1:
			return HttpResponse('',status=404)

		video = results[0]

		# pdb.set_trace()

		if option == 1:
			video.like_count += 1
		elif option == -1:
			video.dislike_count += 1

		video.save()

		return JsonResponse({'like':video.like_count, 'dislike':video.dislike_count})
	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print "*** print_exception:"
		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
		return HttpResponse('',status=500)


# Recommend videos in player page. So users can play at their own interest
@csrf_exempt
def recommend(request):
	try:
		MAX_NUM = 10

		video_id = int(request.POST['id'])

		print 'recommend:',video_id

		video = Video.objects.get(video_id=video_id)

		vidList = []
		checkSet = set()
		checkSet.add(video_id)
		# First, look for videos in the same directory

		file_name_reg = re.compile(r'(.*)/[^/]+$', re.UNICODE | re.IGNORECASE)
		dir = file_name_reg.search(video.path).groups()[0]

		print 'File Dir:',dir
		print '#1:Search in dir'
		#BUG BUG: Bug here
		if len(dir)>0:
			videosInSameDir = Video.objects.filter(path__contains=dir)
			for vid in videosInSameDir:
				if vid.video_id not in checkSet:
					checkSet.add(vid.video_id)
					vidList.append(dictForVideo(vid))

		for item in vidList:
			print item

		print '#2:Keywords related'
		# pdb.set_trace()
		if len(vidList) < MAX_NUM:
			# Second, look for videos with similar keywords
			keywords = KeywordVideoId.objects.filter(video_id=video_id)
			for record in keywords:
				keyword = record.keyword
				videos = KeywordVideoId.objects.filter(keyword=keyword)
				for vid in videos:
					if vid.video_id not in checkSet:
						checkSet.add(vid.video_id)
						video = Video.objects.get(video_id=video_id)
						vidList.append(dictForVideo(video))
			# Third, look for recently added
			print '#3:Look for recent videos'
			if len(vidList) < MAX_NUM:
				recentRecords = loadRecentRecords()
				for record in recentRecords:
					if record.id not in checkSet:
						checkSet.add(record.id)
						vidList.append(record)
		# Trim if necessary
		if len(vidList) > MAX_NUM:
			vidList = vidList[0:MAX_NUM]

		return JsonResponse({'videos':vidList})
	except Exception as e:
		return HttpResponse('', status=500)