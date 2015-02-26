from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from video.models import Video


urlpatterns = patterns('regular_users_interface.views',
    url(r'^$', 'dashboard', name='user_dashboard'),
    url(r'^(?P<pk>\d+)/$', login_required(DetailView.as_view(model=Video, template_name="regular_users_interface/video_detail.haml")), name='user_video_detail'),
)
