from django.shortcuts import render
from django.http.response import HttpResponse

def index(request):
	return HttpResponse('live index not yet implemented')

def live(request, live_id):
	return HttpResponse('live to be implemented')

def post(request, live_id):
	return HttpResponse('live-post to be implemented')