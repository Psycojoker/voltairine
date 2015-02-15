from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'soya.views.home_redirect', name='home_redirect'),
    url(r'^accounts/', include('authentification.urls')),
    url(r'^administration/', include('administration.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
