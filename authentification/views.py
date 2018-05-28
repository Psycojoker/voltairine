# encoding: utf-8

from django.contrib.auth.views import login as base_login, PasswordResetView
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect

from .forms import PasswordResetUserDontExistsForm


def login(request):
    return base_login(request, template_name="registration/login.haml")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")


class PasswordResetUserDontExistsView(PasswordResetView):
    form_class = PasswordResetUserDontExistsForm
    email_template_name = 'registration/password_reset_email_saya.html'
    from_email = "noreply@sayaplay.fr"
