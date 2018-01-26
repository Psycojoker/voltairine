from django.conf.urls import url
from hamlpy.views.generic import DetailView

from .models import VideoShare


urlpatterns = [
    url(r'^video/(?P<pk>[a-zA-Z0-9]+)/$', DetailView.as_view(model=VideoShare), name='video_share_detail'),
]
