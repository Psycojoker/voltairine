import os
import shutil

from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django import forms

from administration.utils import is_staff

from resumable.fields import ResumableFileField

from sections.models import SubSubSection, VideoSection
from video.models import Video


class ResumableForm(forms.Form):
    title = forms.CharField()
    file_name = ResumableFileField(upload_url=reverse_lazy('upload'), chunks_dir="chuncks")
    subsubsection = forms.ModelChoiceField(queryset=SubSubSection.objects.filter(subsection__section="1"), required=False)


@is_staff
def upload_video(request):
    if request.method == "GET":
        return render(request, "upload/upload.haml", {"form": ResumableForm()})

    assert request.method == "POST"

    # POST
    form = ResumableForm(request.POST)
    if not form.is_valid():
        return render(request, "upload/upload.haml", {"form": form})

    destination = os.path.join(settings.MEDIA_ROOT, "videos")

    if not os.path.exists(destination):
        os.makedirs(destination)

    shutil.move(form.cleaned_data["file_name"].file.name, destination)

    video = Video.objects.create(
        title=form.cleaned_data["title"],
        file_name=os.path.split(form.cleaned_data["file_name"].file.name)[1],
    )

    if form.cleaned_data["subsubsection"]:
        VideoSection.objects.create(
            video=video,
            subsubsection=form.cleaned_data["subsubsection"],
        )

    return HttpResponseRedirect(reverse("administration_video_detail", args=(video.pk,)))
