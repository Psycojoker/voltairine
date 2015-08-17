import os
import shutil

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import slugify

from administration.utils import user_can_see_administration_interface

from sections.models import VideoSection, Section
from video.models import Video
from video.utils import generate_random_id_for_video

from .utils import generate_random_string
from .forms import ResumableForm


@user_can_see_administration_interface
def upload_video(request):
    if request.method == "GET":
        form = ResumableForm()

        if not request.user.is_staff:
            form["section"].field.queryset = Section.objects.filter(pk__in=map(lambda x: x.pk, request.user.sections_can_administrate()))
            form["section"].field.required = True
            form["section"].field.empty_label = None

        return render(request, "upload/upload.haml", {"form": form})

    assert request.method == "POST"

    # POST
    form = ResumableForm(request.POST)

    # bad: not dry
    if not request.user.is_staff:
        form["section"].field.queryset = Section.objects.filter(pk__in=map(lambda x: x.pk, request.user.sections_can_administrate()))
        form["section"].field.required = True
        form["section"].field.empty_label = None

    if not form.is_valid():
        return HttpResponseBadRequest("%s" % form.errors)

    if not request.user.is_staff:
        assert form.cleaned_data["section"] in request.user.sections_can_administrate()

    destination = os.path.join(settings.MEDIA_ROOT, "videos")

    if not os.path.exists(destination):
        os.makedirs(destination)

    full_path_file_name = form.cleaned_data["file_name"].file.name
    file_name = os.path.split(full_path_file_name)[1]

    # remove anything special from file name, avoid strange bugs
    if "." in file_name:
        file_name = slugify(".".join(file_name.split(".")[:-1])) + "." + file_name.split(".")[-1]
    else:  # strange, no extension situation
        file_name = slugify(file_name)

    # ensure file_name is uniq
    # not the best strategy, but good enough
    # shouldn't loop more than 1 time, maybe 2-3 in the worst situation
    while os.path.exists(os.path.join(destination, file_name)):
        file_name = file_name.split(".")
        assert len(file_name) > 0
        if len(file_name) > 1:
            file_name.insert(-1, generate_random_string(10))
            file_name = ".".join(file_name)
        else:
            file_name = "%s_%s" % (file_name[0], generate_random_string(10))

    shutil.move(full_path_file_name, os.path.join(destination, file_name))

    video = Video.objects.create(
        title=form.cleaned_data["title"],
        file_name=file_name,
        random_id=generate_random_id_for_video(),
    )

    if form.cleaned_data["section"]:
        VideoSection.objects.create(
            video=video,
            section=form.cleaned_data["section"],
        )

    if request.is_ajax():
        return HttpResponse("ok")

    return HttpResponseRedirect(reverse("administration_video_detail", args=(video.pk,)))
