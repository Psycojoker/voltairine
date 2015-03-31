from django.conf.urls import patterns, url
from resumable.views import ResumableUploadView

from administration.utils import user_can_see_administration_interface


urlpatterns = patterns('upload_video.views',
    url(r'^upload/$', user_can_see_administration_interface(ResumableUploadView.as_view()), name='upload'),
    url(r'^upload_page/$', 'upload_video', name='upload_video'),
)
