from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from .views import home_redirect

urlpatterns = [
    url(r'^$', home_redirect, name='home_redirect'),
    url(r'^accounts/', include('authentification.urls')),
    url(r'^administration/', include('administration.urls')),
    url(r'^films/', include('regular_users_interface.urls')),
    url(r'^share/', include('video_share.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
