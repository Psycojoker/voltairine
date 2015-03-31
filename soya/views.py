from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def home_redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('administration_dashboard'))
    if request.user.group_is_admin_set.exists():
        return HttpResponseRedirect(reverse('administration_dashboard'))
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_dashboard'))
    return HttpResponseRedirect(reverse('login'))
