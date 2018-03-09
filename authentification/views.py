# encoding: utf-8

from django.contrib.auth.views import login as base_login
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context

from .forms import ForgottenPasswordForm


def login(request):
    return base_login(request, template_name="registration/login.haml")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")
