from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def home_redirect(request):
    return HttpResponseRedirect(reverse('login'))
