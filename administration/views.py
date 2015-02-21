from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.models import User

from sections.models import SubSection, SubSubSection

from .utils import is_staff


class CreateUser(CreateView):
    model=User
    template_name='administration/user_update_form.haml'
    fields=['username', 'password', 'is_staff', 'first_name', 'last_name', 'email']

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))


class CreateSubSection(CreateView):
    model=SubSection
    template_name='administration/section_list.haml'
    fields=['title', 'section']
    success_url=reverse_lazy('administration_section_list')


class CreateSubSubSection(CreateView):
    model=SubSubSection
    template_name='administration/section_list.haml'
    fields=['title', 'subsection']
    success_url=reverse_lazy('administration_section_list')


class UpdateUser(UpdateView):
    model=User
    template_name='administration/user_update_form.haml'
    fields=['username', 'first_name', 'last_name', 'email']

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))


@is_staff
def dashboard(request):
    return render(request, "administration/dashboard.haml")
