from django.shortcuts import render
from django.db.models import Q
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from video.models import Video
from sections.models import Section

from sections.utils import unfold_tree


@login_required
def dashboard(request):
    # no, that was not easy to write at all
    all_sections = Section.objects.prefetch_related("videosection_set__video")
    node_to_childrens = unfold_tree(all_sections.as_python_tree())
    section_user_has_access_to = Section.objects.filter(Q(permission__user=request.user)|Q(group__users=request.user))

    sections_I_can_read = set()

    for i in section_user_has_access_to:
        sections_I_can_read.add(i)
        map(sections_I_can_read.add, node_to_childrens[i])

    section_list = []

    for section in all_sections:
        if section in sections_I_can_read or set(node_to_childrens[section]) & sections_I_can_read:
            section_list.append(section)

    return render(request, 'regular_users_interface/dashboard.haml', {
        "sections_I_can_read": sections_I_can_read,
        "section_list": section_list,
        "level": 1,
    })


class UserVideoDetail(DetailView):
    model = Video
    template_name = "regular_users_interface/video_detail.haml"

    def get(self, request, *args, **kwargs):
        to_return = super(UserVideoDetail, self).get(request, *args, **kwargs)

        section_user_has_access_to = Section.objects.filter(Q(permission__user=request.user)|Q(group__users=request.user)).prefetch_related("children")

        sections_I_can_read = set()

        for i in section_user_has_access_to:
            sections_I_can_read.add(i)
            map(sections_I_can_read.add, i.children.all())

        if not Section.objects.filter(videosection__video=self.object).filter(id__in=map(lambda x: x.pk, sections_I_can_read)).exists():
            raise PermissionDenied()

        return to_return
