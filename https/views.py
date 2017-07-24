# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


# Create your views here.
def certificate_download(request):
    return render(request, 'cert.html')
