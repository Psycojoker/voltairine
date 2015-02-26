from django.http import HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User


from sections.models import SubSection, SubSubSection, Permission

from .forms import PermissionForm
from .utils import is_staff


class DetailUser(DetailView):
    model=User
    template_name='administration/user_detail.haml'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailUser, self).get_context_data(*args, **kwargs)
        context["subsection_list"] = SubSection.objects.all()
        return context


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
    fields=['username', 'first_name', 'last_name', 'email', 'is_staff']

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))


@is_staff
def dashboard(request):
    return render(request, "administration/dashboard.haml")


@is_staff
@require_POST
def change_subsection_permission(request):
    form = PermissionForm(request.POST)

    if not form.is_valid():
        # sucks for debugging
        print form.errors
        raise PermissionDenied()

    if form.cleaned_data["state"]:
        assert not Permission.objects.filter(
            user=form.cleaned_data["user"],
            subsubsection=form.cleaned_data["subsubsection"],
        ).exists()

        # autorised
        Permission.objects.create(
            user=form.cleaned_data["user"],
            subsubsection=form.cleaned_data["subsubsection"],
        )

        return HttpResponse("ok")

    # state is False
    Permission.objects.get(
        user=form.cleaned_data["user"],
        subsubsection=form.cleaned_data["subsubsection"],
    ).delete()

    return HttpResponse("ok")
