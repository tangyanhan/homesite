from django.http.response import HttpResponse


def index(request):
    return HttpResponse('live index not yet implemented', status=501)


def live(request, live_id):
    return HttpResponse('live to be implemented', status=501)


def post(request, live_id):
    return HttpResponse('live-post to be implemented', status=501)
