from django.conf.urls import url
from django.template.defaultfilters import slugify

from resumable.views import ResumableUploadView
from resumable.files import ResumableFile

from administration.utils import user_can_see_administration_interface
from .views import upload_video


@property
def filename(self):
    """Gets the filename."""
    filename = self.kwargs.get('resumableFilename')
    if '/' in filename:
        raise Exception('Invalid filename')
    extension = filename.split(".")[-1]
    return slugify("%s_%s" % (
        self.kwargs.get('resumableTotalSize'),
        ".".join(filename.split(".")[:-1])
    )) + "." + extension

ResumableFile.filename = filename


urlpatterns = [
    url(r'^upload/$', user_can_see_administration_interface(ResumableUploadView.as_view()), name='upload'),
    url(r'^upload_page/$', upload_video, name='upload_video'),
]
