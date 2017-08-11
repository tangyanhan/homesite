"""homesite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import include

import settings

from video import video_stream
from video import views as video_views
from video import player_view

import https.views as https_views

urlpatterns = [
                  url(r'^$', video_views.videos, name='video-index'),
                  # Player View
                  url(r'^play/([a-f0-9]+)$', player_view.play, name='play'),
                  url(r'^rate/', player_view.rate, name='rate-video'),
                  url(r'^recommend/', player_view.recommend, name='recommend-videos'),
                  url(r'^stream/([a-f0-9]+)$', video_stream.stream, name='stream'),
                  url(r'^search.*$', video_views.videos, name='search'),
                  url(r'^suggest/$', video_views.keyword_suggest, name='keyword_suggest'),
                  url(r'^rating_detail/$', video_views.rating_detail, name='rating-detail'),
                  url(r'^admin/', admin.site.urls, name='admin'),
                  url(r'^manage/', include('manage_videos.urls', namespace='manage')),
                  url(r'^accounts/login/$', auth_views.login, {'template_name': 'login.html'}),
                  url(r'^cert/', https_views.certificate_download, name='cert'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'video.views.handler404'
handler500 = 'video.views.handler500'
