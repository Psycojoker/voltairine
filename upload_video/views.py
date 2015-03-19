import os
import shutil

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

from administration.utils import is_staff

from sections.models import VideoSection
from video.models import Video

from .utils import generate_random_string
from .forms import ResumableForm


@is_staff
def upload_video(request):
    if request.method == "GET":
        return render(request, "upload/upload.haml", {"form": ResumableForm()})

    assert request.method == "POST"

    # POST
    form = ResumableForm(request.POST)
    if not form.is_valid():
        return render(request, "upload/upload.haml", {"form": form}, status=400)

    destination = os.path.join(settings.MEDIA_ROOT, "videos")

    if not os.path.exists(destination):
        os.makedirs(destination)

    full_path_file_name = form.cleaned_data["file_name"].file.name
    file_name = os.path.split(full_path_file_name)[1]

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
    )

    if form.cleaned_data["section"]:
        VideoSection.objects.create(
            video=video,
            section=form.cleaned_data["section"],
        )

    if request.is_ajax():
        return HttpResponse("ok")

    return HttpResponseRedirect(reverse("administration_video_detail", args=(video.pk,)))
