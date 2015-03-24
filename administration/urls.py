from django.conf.urls import patterns, url, include
from django.views.generic import ListView, DetailView

from sections.models import Section
from permissions_groups.models import Group

from .views import UpdateUser, CreateUser, CreateSection, DetailUser, DeleteUser, UpdateSection, DeleteVideo, CreateGroup
from .utils import is_staff


urlpatterns = patterns('administration.views',
    url(r'^$', 'dashboard', name='administration_dashboard'),
    url(r'^user/$', 'user_and_groups', name='administration_user_list'),
    url(r'^user/new/$', is_staff(CreateUser.as_view()), name='administration_user_create'),
    url(r'^user/(?P<pk>\d+)/$', is_staff(DetailUser.as_view()), name='administration_user_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', is_staff(UpdateUser.as_view()), name='administration_user_update'),
    url(r'^user/(?P<pk>\d+)/delete/$', is_staff(DeleteUser.as_view()), name='administration_user_delete'),

    url(r'^group/new/$', is_staff(CreateGroup.as_view()), name='administration_group_create'),
    url(r'^group/(?P<pk>\d+)/$', is_staff(DetailView.as_view(model=Group, template_name="administration/group_detail.haml")), name='administration_group_detail'),

    url(r'^section/$', is_staff(ListView.as_view(model=Section, template_name='administration/section_list.haml')), name='administration_section_list'),
    url(r'^section/new/$', is_staff(CreateSection.as_view()), name='administration_section_create'),
    url(r'^section/(?P<pk>\d+)/update/$', is_staff(UpdateSection.as_view()), name='administration_section_update'),
    url(r'^section/(?P<pk>\d+)/delete/$', 'delete_section_and_childrens', name='administration_section_delete'),

    url(r'^change_subsection_permission/$', 'change_section_permission', name='administration_change_subsection_permission'),

    url(r'^video/$', 'video_list', name='administration_video_list'),
    url(r'^video/(?P<pk>\d+)/$', 'video_detail', name='administration_video_detail'),
    url(r'^video/(?P<pk>\d+)/delete/$', is_staff(DeleteVideo.as_view()), name='administration_video_delete'),

    url(r'^', include('upload_video.urls')),
)
