#coding=utf-8

import time
import json

from django.shortcuts import render
from httplib import HTTPConnection


# Create your views here.
def weather(request):
    # try:
    timestamp = int(time.time() * 1000)
    city_code = '101190401'

    path_format = '/dingzhi/[city].html?_=[time]'
    path = path_format.replace('[city]',city_code).replace('[time]', str(timestamp))

    ref_format = 'http://www.weather.com.cn/weather/[city].shtml'
    referer = ref_format.replace('[city]', city_code)

    conn = HTTPConnection('d1.weather.com.cn')
    conn.request('GET',path,headers={'Referer':referer})
    response = conn.getresponse()
    data = response.read()

    data = unicode(data,encoding='utf-8')
    json_start_idx = data.find('{')
    json_end_idx = data.rfind(';var')

    if json_start_idx == -1:
        return render(request, 'weather.html', {'data':data}, status=400)

    data = data[json_start_idx:json_end_idx]
    return render(request, 'weather.html', {'data':data}, status=200)
    #
    # except:
    #     return render(request, 'weather.html', {'data':''}, status=500)
