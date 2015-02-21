from django.conf.urls import patterns, url


urlpatterns = patterns('regular_users_interface.views',
    url(r'^$', 'dashboard', name='user_dashboard'),
)
