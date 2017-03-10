from django.shortcuts import render
from django.http.response import HttpResponse

# Create your views here.
def live(request, live_id):
	return HttpResponse('live to be implemented')

def post(request, live_id):
	return HttpResponse('live-post to be implemented')