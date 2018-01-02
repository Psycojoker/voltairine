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


# XXX this is not used anymore
def forgotten_password(request):
    if request.method == 'GET':
        return render(request, 'registration/forgotten_password.haml', {"form": ForgottenPasswordForm()})

    form = ForgottenPasswordForm(request.POST)

    if not form.is_valid():
        return render(request, 'registration/forgotten_password.haml', {"form": form})

    send_mail(
              u'Demande de mot de passe oublié par %s pour %s' % (form.cleaned_data['email'], form.cleaned_data['username']),
              get_template('registration/forgotten_password_email.txt').render(Context(form.cleaned_data)),
              'noreply@play.saya.fr',
              settings.SAYA_FORGOTTEN_PASSWORD_EMAILS,
              fail_silently=False
    )

    return HttpResponseRedirect(reverse('forgotten_password_success'))
