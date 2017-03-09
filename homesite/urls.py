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

import settings

from video import video_stream
from video import views as video_views

urlpatterns = [
		url(r'^$', video_views.videos, name='video-index'),
		url(r'^play/([a-f0-9]+)$', video_views.play,name='play'),
		url(r'^stream/([a-f0-9]+)$', video_stream.stream, name='stream'),
		url(r'^search.*$', video_views.videos, name='search'),
		url(r'^suggest/', video_views.keyword_suggest, name='keyword_suggest'),
		url(r'^admin/', admin.site.urls),
			] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
