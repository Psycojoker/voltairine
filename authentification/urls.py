from django.conf.urls import patterns, url


urlpatterns = patterns('authentification.views',
    url(r'^login/', 'login', name='login'),
    url(r'^logout/', 'logout', name='logout'),
    url(r'^forgotten_password/', 'forgotten_password', name='forgotten_password'),
)
