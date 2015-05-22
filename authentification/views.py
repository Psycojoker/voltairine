from django.contrib.auth.views import login as base_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import ForgottenPasswordForm


def login(request):
    return base_login(request, template_name="registration/login.haml")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")


def forgotten_password(request):
    if request.method == 'GET':
        return render(request, 'registration/forgotten_password.haml', {"form": ForgottenPasswordForm()})

    form = ForgottenPasswordForm(request.POST)

    if not form.is_valid():
        return render(request, 'registration/forgotten_password.haml', {"form": form})
