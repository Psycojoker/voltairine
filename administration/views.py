from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User


class UpdateUser(UpdateView):
    model=User
    template_name='administration/user_update_form.haml'
    fields=['username', 'first_name', 'last_name', 'email']

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))


def dashboard(request):
    return render(request, "administration/dashboard.haml")
