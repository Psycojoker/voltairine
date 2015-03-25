from django import forms
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import UpdateView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

from sections.models import Section, Permission, VideoSection
from video.models import Video
from permissions_groups.models import Group

from .forms import UserPermissionForm, GroupPermissionForm, VideoForm, FormUser
from .utils import is_staff


@is_staff
def user_and_groups(request):
    return render(request, "administration/user_list.haml", {
        "user_list": User.objects.all(),
        "group_list": Group.objects.all(),
    })


class DetailUser(DetailView):
    model = User
    template_name = 'administration/user_detail.haml'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailUser, self).get_context_data(*args, **kwargs)
        context["section_list"] = Section.objects.all()
        return context


class CreateUser(CreateView):
    model = User
    template_name = 'administration/user_update_form.haml'
    fields = ['username', 'password', 'is_staff', 'first_name', 'last_name', 'email']

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))

    def form_valid(self, form):
        to_return = super(CreateUser, self).form_valid(form)
        self.object.set_password(form.cleaned_data["password"])
        self.object.save()
        return to_return


class UpdateUser(UpdateView):
    model = User
    template_name = 'administration/user_update_form.haml'
    form_class = FormUser

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))

    def form_valid(self, form):
        old_password_hash = self.object.password
        to_return = super(UpdateView, self).form_valid(form)
        if form.cleaned_data["password"]:
            self.object.set_password(form.cleaned_data["password"])
        else:
            self.object.password = old_password_hash
        self.object.save()
        return to_return


class DeleteUser(DeleteView):
    model = User
    template_name = "administration/user_confirm_delete.haml"
    success_url = reverse_lazy('administration_user_list')


class CreateGroup(CreateView):
    model = Group
    template_name = 'administration/group_update_form.haml'
    form_class = modelform_factory(Group,
        widgets={
            "admins": forms.CheckboxSelectMultiple,
            "users": forms.CheckboxSelectMultiple,
        },
        fields=['name', 'users', 'admins']
    )

    def get_success_url(self):
        return reverse('administration_group_detail', args=(self.object.pk,))


class DetailGroup(DetailView):
    model = Group
    template_name = 'administration/group_detail.haml'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailGroup, self).get_context_data(*args, **kwargs)
        context["section_list"] = Section.objects.all()
        return context


class UpdateGroup(UpdateView):
    model = Group
    template_name = 'administration/group_update_form.haml'
    form_class = modelform_factory(Group,
        widgets={
            "admins": forms.CheckboxSelectMultiple,
            "users": forms.CheckboxSelectMultiple,
        },
        fields=['name', 'users', 'admins']
    )

    def get_success_url(self):
        return reverse('administration_group_detail', args=(self.object.pk,))


class DeleteGroup(DeleteView):
    model = Group
    template_name = "administration/group_confirm_delete.haml"
    success_url = reverse_lazy('administration_user_list')


class CreateSection(CreateView):
    model = Section
    template_name = 'administration/section_list.haml'
    fields = ['title', 'parent']
    success_url = reverse_lazy('administration_section_list')


class UpdateSection(UpdateView):
    model = Section
    template_name = 'administration/section_list.haml'
    fields = ['title']
    success_url = reverse_lazy('administration_section_list')


@is_staff
def delete_section_and_childrens(request, pk):
    get_object_or_404(Section, pk=pk).delete()
    return HttpResponseRedirect((reverse('administration_section_list')))


class DeleteVideo(DeleteView):
    model = Video
    template_name = "administration/video_confirm_delete.haml"
    success_url = reverse_lazy('administration_video_list')


@is_staff
def dashboard(request):
    return render(request, "administration/dashboard.haml")


@is_staff
@require_POST
def change_user_section_permission(request):
    form = UserPermissionForm(request.POST)

    if not form.is_valid():
        # sucks for debugging
        print form.errors
        raise PermissionDenied()

    if form.cleaned_data["state"]:
        # already have the autorisation, don't do anything
        if Permission.objects.filter(user=form.cleaned_data["user"], section=form.cleaned_data["section"]).exists():
            return HttpResponse("ok")

        # autorised
        Permission.objects.create(
            user=form.cleaned_data["user"],
            section=form.cleaned_data["section"],
        )

        return HttpResponse("ok")

    if not Permission.objects.filter(user=form.cleaned_data["user"], section=form.cleaned_data["section"]).exists():
        # don't have the permission, don't do anything
        return HttpResponse("ok")

    # state is False
    Permission.objects.get(
        user=form.cleaned_data["user"],
        section=form.cleaned_data["section"],
    ).delete()

    return HttpResponse("ok")


@is_staff
@require_POST
def change_group_section_permission(request):
    form = GroupPermissionForm(request.POST)

    if not form.is_valid():
        # sucks for debugging
        print form.errors
        raise PermissionDenied()

    group = form.cleaned_data["group"]
    section_id = form.cleaned_data["section"].id

    if form.cleaned_data["state"]:
        # already have the autorisation, don't do anything
        if group.permissions.filter(id=section_id).exists():
            return HttpResponse("ok")

        # autorised
        group.permissions.add(section_id)

        return HttpResponse("ok")

    if not group.permissions.filter(id=section_id).exists():
        # don't have the permission, don't do anything
        return HttpResponse("ok")

    # state is False
    group.permissions.remove(section_id)

    return HttpResponse("ok")


@is_staff
def video_list(request):
    return render(request, 'administration/video_list.haml', {
        "level": 1,
        "section_list": Section.objects.all(),
        "video_list": Video.objects.filter(videosection__isnull=True),
    })


@is_staff
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)

    if request.method == "POST":
        form = VideoForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()

        video.title = form.cleaned_data["title"]
        video.film_name = form.cleaned_data["film_name"]
        video.realisation = form.cleaned_data["realisation"]
        video.production = form.cleaned_data["production"]
        video.photo_direction = form.cleaned_data["photo_direction"]
        video.observations = form.cleaned_data["observations"]

        if form.cleaned_data["section"]:
            if not hasattr(video, "videosection"):
                VideoSection.objects.create(
                    video=video,
                    section=form.cleaned_data["section"],
                )
            elif video.videosection.section != form.cleaned_data["section"]:
                video.videosection.delete()
                VideoSection.objects.create(
                    video=video,
                    section=form.cleaned_data["section"],
                )
        elif form.cleaned_data["section"] is None and hasattr(video, "ection"):
            video.videosection.delete()
            # need to do that, the instance isn't modified by the previous line
            del video.videosection

        video.save()
        return HttpResponse(video.videosection.__unicode__() if hasattr(video, "videosection") else "")

    return render(request, "administration/video_detail.haml", {
        "object": video,
        "form": VideoForm(),
    })
