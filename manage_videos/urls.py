from django.conf.urls import url

from . import views

app_name='manage'
urlpatterns = [
	url(r'^index/$', views.index, name='index'),
	url(r'^db/(\w+)/$', views.db, name='db'),
	url(r'^import/$', views.import_videos, name='import'),
	url(r'^import/dir$', views.load_dir, name='dir')
]
