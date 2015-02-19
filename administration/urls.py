from django.conf.urls import patterns, url, include
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User

from sections.models import SubSection
from video.models import Video

from .views import UpdateUser, CreateUser, CreateSubSection, CreateSubSubSection


urlpatterns = patterns('administration.views',
    url(r'^$', 'dashboard', name='administration_dashboard'),
    url(r'^user/$', ListView.as_view(model=User, template_name='administration/user_list.haml'), name='administration_user_list'),
    url(r'^user/new/$', CreateUser.as_view(), name='administration_user_create'),
    url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(model=User, template_name='administration/user_detail.haml'), name='administration_user_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', UpdateUser.as_view(), name='administration_user_update'),

    url(r'^section/$', ListView.as_view(model=SubSection, template_name='administration/section_list.haml'), name='administration_section_list'),
    url(r'^section/new/$', CreateSubSection.as_view(), name='administration_section_create'),
    url(r'^subsubsection/new/$', CreateSubSubSection.as_view(), name='administration_section_create'),

    url(r'^video/$', ListView.as_view(model=Video, template_name='administration/video_list.haml'), name='administration_video_list'),

    url(r'^', include('upload_video.urls')),
)
