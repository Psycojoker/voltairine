from django.conf.urls import patterns, url, include
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User

from sections.models import SubSection
from video.models import Video

from .views import UpdateUser, CreateUser, CreateSubSection, CreateSubSubSection, DetailUser
from .utils import is_staff


urlpatterns = patterns('administration.views',
    url(r'^$', 'dashboard', name='administration_dashboard'),
    url(r'^user/$', is_staff(ListView.as_view(model=User, template_name='administration/user_list.haml')), name='administration_user_list'),
    url(r'^user/new/$', is_staff(CreateUser.as_view()), name='administration_user_create'),
    url(r'^user/(?P<pk>\d+)/$', is_staff(DetailUser.as_view()), name='administration_user_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', is_staff(UpdateUser.as_view()), name='administration_user_update'),

    url(r'^section/$', is_staff(ListView.as_view(model=SubSection, template_name='administration/section_list.haml')), name='administration_section_list'),
    url(r'^section/new/$', is_staff(CreateSubSection.as_view()), name='administration_section_create'),
    url(r'^subsubsection/new/$', is_staff(CreateSubSubSection.as_view()), name='administration_section_create'),

    url(r'^change_subsection_permission/$', 'change_subsection_permission', name='administration_change_subsection_permission'),

    url(r'^video/$', is_staff(ListView.as_view(model=Video, template_name='administration/video_list.haml')), name='administration_video_list'),
    url(r'^video/(?P<pk>\d+)/$', 'video_detail', name='administration_video_detail'),

    url(r'^', include('upload_video.urls')),
)
