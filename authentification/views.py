from django.contrib.auth.views import login as base_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect


def login(request):
    return base_login(request, template_name="registration/login.haml")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")
