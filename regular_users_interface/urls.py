from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import UserVideoDetail, dashboard


urlpatterns = [
    url(r'^$', dashboard, name='user_dashboard'),
    url(r'^(?P<pk>\d+)/$', login_required(UserVideoDetail.as_view()), name='user_video_detail'),
]
