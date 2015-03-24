import operator

from django.shortcuts import render
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from video.models import Video
from sections.models import Section, Permission


@login_required
def dashboard(request):
    # this is just bad but I think that I've just eat the limit of what sql can do
    # still: optimisation can be made (to avoid requiering all the time)
    section_I_can_read = set(reduce(operator.add, map(lambda x: list(x.get_descendants(True)), Section.objects.filter(permission__user=request.user)), []))

    section_list = []

    for section in Section.objects.all():
        if section_I_can_read & set(section.get_descendants(True)):
            section_list.append(section)

    return render(request, 'regular_users_interface/dashboard.haml', {
        "section_list": section_list,
        "section_I_can_read": section_I_can_read,
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
