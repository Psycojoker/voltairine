from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User

from .views import UpdateUser, CreateUser


urlpatterns = patterns('administration.views',
    url(r'^$', 'dashboard', name='administration_dashboard'),
    url(r'^user/$', ListView.as_view(model=User, template_name='administration/user_list.haml'), name='administration_user_list'),
    url(r'^user/new/$', CreateUser.as_view(), name='administration_user_create'),
    url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(model=User, template_name='administration/user_detail.haml'), name='administration_user_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', UpdateUser.as_view(), name='administration_user_update'),
)
