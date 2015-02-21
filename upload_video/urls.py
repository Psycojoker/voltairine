from django.conf.urls import patterns, url
from resumable.views import ResumableUploadView

from administration.utils import is_staff


urlpatterns = patterns('upload_video.views',
    url(r'^upload/$', is_staff(ResumableUploadView.as_view()), name='upload'),
    url(r'^upload_page/$', 'upload_video', name='upload_video'),
)
