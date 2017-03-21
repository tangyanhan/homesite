from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Video
from models import KeywordCount
from models import KeywordVideoId

def play(request,digest):
	return render(request,'video-player.html', {'video':digest, 'thumb':'thumb/'+ digest +'.png'})

@csrf_exempt # TODO: should use auth
def rate(request):
	try:
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
def recommend(request):
    pass