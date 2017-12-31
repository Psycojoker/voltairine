from django.conf.urls import url
from resumable.views import ResumableUploadView

from administration.utils import user_can_see_administration_interface
from .views import upload_video


urlpatterns = [
    url(r'^upload/$', user_can_see_administration_interface(ResumableUploadView.as_view()), name='upload'),
    url(r'^upload_page/$', upload_video, name='upload_video'),
]
