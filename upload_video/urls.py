from django.conf.urls import patterns, url


urlpatterns = patterns('upload_video.views',
    url(r'^upload/$', 'upload_video', name='upload_video'),
)
