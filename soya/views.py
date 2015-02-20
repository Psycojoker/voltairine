from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def home_redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('administration_dashboard'))
    return HttpResponseRedirect(reverse('login'))
