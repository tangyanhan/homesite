from django.conf.urls import url

from . import views

app_name='manage'
urlpatterns = [
	url(r'^index/$', views.index, name='index'),
	url(r'^db/(\w+)/$', views.db, name='db'),
	url(r'^import/index/$', views.import_index, name='import'),
	url(r'^import/dir/$', views.import_dir, name='import-dir'),
	url(r'^import/status/', views.import_status, name='import-status')
]
