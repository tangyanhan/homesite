from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import Http404
from homesite.settings import cfgDict
from video.models import Video
import os
import re

# Create your views here.
def index(request):
    return render(request,'manage-videos.html')

def load_dir(request):

    dir = request.POST['dir']

    if len(dir)>512:
        raise Http404

    upperIdx = dir.find('..')

    if upperIdx != -1:
        # Check if it contains '..' traps. For a sub path combined can be '/home/xxx/../../usr/local'
        if upperIdx != (len(dir)-2):
            raise Http404
        match = re.match(r'(.*)/[^/]+/\.\.$', dir)
        dir = ""
        if match is not None:
            dir = match.groups()[0]

    root = cfgDict['load_dir_root']
    path = os.path.join(root,dir)

    if not os.path.isdir(path):
        raise Http404

    fileList = []
    for file in os.listdir(path):
        if file.startswith('.'):
            continue

        entry = os.path.join(path,file)

        isDir = False
        if os.path.isdir(entry):
            isDir = True
        fileList.append({'file':file,'isdir':isDir})

    currentDir = path[len(root):]
    return JsonResponse({'files':fileList, 'currentDir':currentDir})

def manage_videos(request):
    allvideos = Video.objects.all()
    pass