from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from video.models import Video
from sections.models import Permission


class UserVideoDetail(DetailView):
    model = Video
    template_name = "regular_users_interface/video_detail.haml"

    def get(self, request, *args, **kwargs):
        to_return = super(UserVideoDetail, self).get(request, *args, **kwargs)

        if not Permission.objects.filter(user=request.user, subsubsection__videosection__video=self.object).exists():
            raise PermissionDenied()

        return to_return


urlpatterns = patterns('regular_users_interface.views',
    url(r'^$', 'dashboard', name='user_dashboard'),
    url(r'^(?P<pk>\d+)/$', login_required(UserVideoDetail.as_view()), name='user_video_detail'),
)
