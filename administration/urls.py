from django.conf.urls import url, include

from .views import (UpdateUser, CreateUser, CreateSection, DetailUser,
                    DeleteUser, UpdateSection, DeleteVideo, CreateGroup,
                    UpdateGroup, DeleteGroup, DetailGroup, ListSection,
                    dashboard, user_and_groups, delete_section_and_childrens,
                    change_user_section_permission,
                    change_group_section_permission, video_list, video_detail)
from .utils import user_can_see_administration_interface, user_is_staff


urlpatterns = [
    url(r'^$', dashboard, name='administration_dashboard'),
    url(r'^user/$', user_and_groups, name='administration_user_list'),
    url(r'^user/new/$', user_can_see_administration_interface(CreateUser.as_view()), name='administration_user_create'),
    url(r'^user/(?P<pk>\d+)/$', user_can_see_administration_interface(DetailUser.as_view()), name='administration_user_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', user_can_see_administration_interface(UpdateUser.as_view()), name='administration_user_update'),
    url(r'^user/(?P<pk>\d+)/delete/$', user_can_see_administration_interface(DeleteUser.as_view()), name='administration_user_delete'),

    url(r'^group/new/$', user_is_staff(CreateGroup.as_view()), name='administration_group_create'),
    url(r'^group/(?P<pk>\d+)/$', user_can_see_administration_interface(DetailGroup.as_view()), name='administration_group_detail'),
    url(r'^group/(?P<pk>\d+)/update/$', user_can_see_administration_interface(UpdateGroup.as_view()), name='administration_group_update'),
    url(r'^group/(?P<pk>\d+)/delete/$', user_is_staff(DeleteGroup.as_view()), name='administration_group_delete'),

    url(r'^section/$', user_can_see_administration_interface(ListSection.as_view()), name='administration_section_list'),
    url(r'^section/new/$', user_can_see_administration_interface(CreateSection.as_view()), name='administration_section_create'),
    url(r'^section/(?P<pk>\d+)/update/$', user_can_see_administration_interface(UpdateSection.as_view()), name='administration_section_update'),
    url(r'^section/(?P<pk>\d+)/delete/$', delete_section_and_childrens, name='administration_section_delete'),

    url(r'^change_user_section_permission/$', change_user_section_permission, name='administration_change_user_section_permission'),
    url(r'^change_group_section_permission/$', change_group_section_permission, name='administration_change_group_section_permission'),

    url(r'^video/$', video_list, name='administration_video_list'),
    url(r'^video/(?P<pk>\d+)/$', video_detail, name='administration_video_detail'),
    url(r'^video/(?P<pk>\d+)/delete/$', user_can_see_administration_interface(DeleteVideo.as_view()), name='administration_video_delete'),

    url(r'^', include('upload_video.urls')),
]
