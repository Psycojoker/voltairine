from django.conf.urls import url, include

from .views import login, logout, PasswordResetUserDontExistsView


urlpatterns = [
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^password_reset/$', PasswordResetUserDontExistsView.as_view(), name='password_reset'),
    url(r'^', include('django.contrib.auth.urls')),
]
