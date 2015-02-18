from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.forms import Form

from resumable.fields import ResumableFileField
from resumable.views import ResumableUploadView


class ResumableForm(Form):
    file = ResumableFileField(upload_url=reverse_lazy('upload'), chunks_dir="chuncks")


def upload_video(request):
    if request.method == "POST":
        form = ResumableForm(request.POST)
        print form.is_valid()
    else:
        form = ResumableForm()

    return render(request, "upload/upload.haml", {"form": form})
