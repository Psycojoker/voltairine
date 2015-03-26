from django.shortcuts import render
from django.db.models import Q
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from video.models import Video
from sections.models import Section, Permission

from sections.utils import unfold_tree


@login_required
def dashboard(request):
    node_to_childrens = unfold_tree(Section.objects.all().as_python_tree())
    section_user_has_access_to = Section.objects.filter(Q(permission__user=request.user)|Q(group__users=request.user))

    sections_I_can_read = set()

    for i in section_user_has_access_to:
        map(sections_I_can_read.add, node_to_childrens[i])

    return render(request, 'regular_users_interface/dashboard.haml', {
        "section_list": Section.objects.filter(id__in=map(lambda x: x.id, sections_I_can_read)),
        "level": 1,
    })


class UserVideoDetail(DetailView):
    model = Video
    template_name = "regular_users_interface/video_detail.haml"

    def get(self, request, *args, **kwargs):
        to_return = super(UserVideoDetail, self).get(request, *args, **kwargs)

        if not Permission.objects.filter(user=request.user, section__videosection__video=self.object).exists():
            raise PermissionDenied()

        return to_return
