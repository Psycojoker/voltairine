from django.conf.urls import url
from hamlpy.views.generic import DetailView

from .models import VideoShare


class VideoShareDetailView(DetailView):
    model = VideoShare

    def get_context_data(self, *args, **kwargs):
        context = super(VideoShareDetailView, self).get_context_data(**kwargs)
        context['hide_logout'] = True
        return context


urlpatterns = [
    url(r'^video/(?P<pk>[a-zA-Z0-9]+)/$', VideoShareDetailView.as_view(), name='video_share_detail'),
]
