from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('authentification.views',
    url(r'^login/', 'login', name='login'),
    url(r'^logout/', 'logout', name='logout'),
    url(r'^forgotten_password/success/', TemplateView.as_view(template_name="registration/forgotten_password_success.haml"), name='forgotten_password_success'),
    url(r'^forgotten_password/', 'forgotten_password', name='forgotten_password'),
)
