from django.conf.urls import patterns, url
from .views import ResumableUploadView


urlpatterns = patterns('upload_video.views',
    url(r'^upload/$', ResumableUploadView.as_view(), name='upload'),
    url(r'^upload_page/$', 'upload_video', name='upload_video'),
)
