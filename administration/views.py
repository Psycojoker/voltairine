from django import forms
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import UpdateView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

from sections.models import Section, Permission, VideoSection
from video.models import Video
from permissions_groups.models import Group

from sections.utils import unfold_tree

from .forms import UserPermissionForm, GroupPermissionForm, VideoForm, FormUser, FormUserForGroupAdmin
from .utils import user_can_see_administration_interface, user_is_staff


@user_can_see_administration_interface
def user_and_groups(request):
    if request.user.is_staff:
        return render(request, "administration/user_list.haml", {
            "user_list": User.objects.all(),
            "group_list": Group.objects.all(),
        })

    elif request.user.group_is_admin_set.exists():
        return render(request, "administration/user_list.haml", {
            "user_list": request.user.users_can_administrate(),
            "group_list": request.user.groups_managed_by_user(),
        })

    else:
        raise PermissionDenied()


class DetailUser(DetailView):
    model = User
    template_name = 'administration/user_detail.haml'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailUser, self).get_context_data(*args, **kwargs)
        if not self.request.user.is_staff and self.object not in self.request.user.users_can_administrate():
            raise PermissionDenied()

        if not self.request.user.is_staff:
            context["group_is_admin"] = self.object.group_is_admin_set.filter(pk__in=map(lambda x: x.pk, self.request.user.groups_managed_by_user()))
            context["group_is_member"] = self.object.group_is_member_set.filter(pk__in=map(lambda x: x.pk, self.request.user.groups_managed_by_user()))

        else:
            context["group_is_admin"] = self.object.group_is_admin_set.all()
            context["group_is_member"] = self.object.group_is_member_set.all()
            context["section_list"] = Section.objects.all()
        return context


class CreateUser(CreateView):
    model = User
    template_name = 'administration/user_update_form.haml'
    fields = ['username', 'password', 'is_staff', 'first_name', 'last_name', 'email']

    def get_form(self, form_class):
        # don't have to check if the user is an admin, the decorator in the
        # urls.py have already do that
        if not self.request.user.is_staff:
            form = FormUserForGroupAdmin(**self.get_form_kwargs())
            form["group"].field.queryset = self.request.user.groups_managed_by_user()
            return form

        return super(CreateUser, self).get_form(form_class)

    def get_success_url(self):
        return reverse('administration_user_detail', args=(self.object.pk,))

    def form_valid(self, form):
        with transaction.atomic():
            to_return = super(CreateUser, self).form_valid(form)
            self.object.set_password(form.cleaned_data["password"])
            self.object.save()

            if not self.request.user.is_staff:
                # request.user is admin of only one group
                if not form.cleaned_data["group"]:
                    assert form["group"].field.queryset.first() in self.request.user.groups_managed_by_user()
                    form["group"].field.queryset.first().users.add(self.object)
                else:
                    assert form.cleaned_data["group"] in self.request.user.groups_managed_by_user()
                    form.cleaned_data["group"].users.add(self.object)

        return to_return


class UpdateUser(UpdateView):
    model = User
    template_name = 'administration/user_update_form.haml'
    form_class = FormUser

    def get_object(self, queryset=None):
        object = super(UpdateUser, self).get_object(queryset)
        if not self.request.user.is_staff and object not in self.request.user.users_can_administrate():
            raise PermissionDenied()

        return object

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

    def get_object(self, queryset=None):
        object = super(DeleteUser, self).get_object(queryset)
        if not self.request.user.is_staff and object not in self.request.user.users_can_administrate():
            raise PermissionDenied()

        return object


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
    queryset = Group.objects.prefetch_related("permissions")
    template_name = 'administration/group_detail.haml'

    def get_object(self, queryset=None):
        object = super(DetailGroup, self).get_object(queryset)
        if not self.request.user.is_staff and object not in self.request.user.groups_managed_by_user():
            raise PermissionDenied()

        return object

    def get_context_data(self, *args, **kwargs):
        context = super(DetailGroup, self).get_context_data(*args, **kwargs)
        if self.request.user.is_staff:
            context["section_list"] = Section.objects.all()
        else:
            sections_tree = Section.objects.all().as_python_tree()
            node_to_childrens = unfold_tree(sections_tree)

            sections_of_group = self.object.permissions.all()
            childrens = set(sum([node_to_childrens[x] for x in sections_of_group], []))
            # in the sections that are directly assigned to the group admin
            # some may be children of others, I don't want them because that
            # would break the display
            context["section_list"] = [(section, node_to_childrens[section]) for section in self.object.permissions.exclude(pk__in=[x.pk for x in childrens])]
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

    def form_valid(self, form):
        if not self.request.user.is_staff and not self.request.user in form.cleaned_data["admins"]:
            form.cleaned_data["admins"] = list(form.cleaned_data["admins"]) + [self.request.user]
        to_return = super(UpdateGroup, self).form_valid(form)
        return to_return

    def get_object(self, queryset=None):
        object = super(UpdateGroup, self).get_object(queryset)
        if not self.request.user.is_staff and object not in self.request.user.groups_managed_by_user():
            raise PermissionDenied()

        return object

    def get_success_url(self):
        return reverse('administration_group_detail', args=(self.object.pk,))


class DeleteGroup(DeleteView):
    model = Group
    template_name = "administration/group_confirm_delete.haml"
    success_url = reverse_lazy('administration_user_list')


class ListSection(ListView):
    model = Section
    template_name = 'administration/section_list.haml'

    def get_context_data(self, *args, **kwargs):
        context = super(ListSection, self).get_context_data(*args, **kwargs)
        if self.request.user.is_staff:
            context["top_section_list"] = [context["section_list"]]
        else:
            sections_tree = Section.objects.all().as_python_tree()
            node_to_childrens = unfold_tree(sections_tree)

            sections_of_groups = Section.objects.filter(group__admins=self.request.user)
            childrens = set(sum([node_to_childrens[x] for x in sections_of_groups], []))
            # in the sections that are directly assigned to the group admin
            # some may be children of others, I don't want them because that
            # would break the display
            context["top_section_list"] = [[section] + node_to_childrens[section] for section in sections_of_groups.exclude(pk__in=[x.pk for x in childrens])]

        return context


class CreateSection(CreateView):
    model = Section
    template_name = 'administration/section_list.haml'
    fields = ['title', 'parent']
    success_url = reverse_lazy('administration_section_list')

    def form_valid(self, form):
        if not self.request.user.is_staff and form.cleaned_data["parent"] not in self.request.user.sections_can_administrate():
            raise PermissionDenied()

        return super(CreateSection, self).form_valid(form)


class UpdateSection(UpdateView):
    model = Section
    template_name = 'administration/section_list.haml'
    fields = ['title']
    success_url = reverse_lazy('administration_section_list')

    def form_valid(self, form):
        if not self.request.user.is_staff and self.object not in self.request.user.sections_can_administrate():
            raise PermissionDenied()

        return super(UpdateSection, self).form_valid(form)


@user_can_see_administration_interface
def delete_section_and_childrens(request, pk):
    section = get_object_or_404(Section, pk=pk)

    if not request.user.is_staff and section not in request.user.sections_can_administrate():
        raise PermissionDenied()

    section.delete()
    return HttpResponseRedirect((reverse('administration_section_list')))


@user_can_see_administration_interface
def dashboard(request):
    return render(request, "administration/dashboard.haml")


@user_is_staff
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


@user_is_staff
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


@user_can_see_administration_interface
def video_list(request):
    if not request.user.is_staff:
        sections_tree = Section.objects.prefetch_related("videosection_set__video").as_python_tree()
        node_to_childrens = unfold_tree(sections_tree)

        sections_of_groups = Section.objects.filter(group__admins=request.user).prefetch_related("videosection_set__video")
        childrens = set(sum([node_to_childrens[x] for x in sections_of_groups], []))
        # in the sections that are directly assigned to the group admin
        # some may be children of others, I don't want them because that
        # would break the display
        return render(request, 'administration/video_list.haml', {
            "level": 1,
            "top_section_list": [[section] + node_to_childrens[section] for section in sections_of_groups.exclude(pk__in=[x.pk for x in childrens])],
            "video_list": [],
        })

    return render(request, 'administration/video_list.haml', {
        "level": 1,
        "top_section_list": [Section.objects.prefetch_related("videosection_set__video")],
        "video_list": Video.objects.filter(videosection__isnull=True),
    })


@user_can_see_administration_interface
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)

    if not request.user.is_staff and video not in request.user.videos_can_administrate():
        raise PermissionDenied()

    if request.method == "POST":
        form = VideoForm(request.POST)

        if not request.user.is_staff:
            form["section"].field.queryset = Section.objects.filter(pk__in=map(lambda x: x.pk, request.user.sections_can_administrate()))
            form["section"].field.required = True
            form["section"].field.empty_label = None

        if not form.is_valid():
            return HttpResponseBadRequest()

        video.title = form.cleaned_data["title"]
        video.film_name = form.cleaned_data["film_name"]
        video.realisation = form.cleaned_data["realisation"]
        video.production = form.cleaned_data["production"]
        video.photo_direction = form.cleaned_data["photo_direction"]
        video.lto_archive_number = form.cleaned_data["lto_archive_number"]
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

    form = VideoForm()

    # not dry
    if not request.user.is_staff:
        form["section"].field.queryset = Section.objects.filter(pk__in=map(lambda x: x.pk, request.user.sections_can_administrate()))
        form["section"].field.required = True
        form["section"].field.empty_label = None

    return render(request, "administration/video_detail.haml", {
        "object": video,
        "form": form,
    })


class DeleteVideo(DeleteView):
    model = Video
    template_name = "administration/video_confirm_delete.haml"
    success_url = reverse_lazy('administration_video_list')

    def get_object(self, queryset=None):
        object = super(DeleteVideo, self).get_object(queryset=queryset)

        if not self.request.user.is_staff and object not in self.request.user.videos_can_administrate():
            raise PermissionDenied()

        return object
