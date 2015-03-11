from django import forms
from django.core.urlresolvers import reverse_lazy

from resumable.fields import ResumableFileField

from sections.models import Section


class ResumableForm(forms.Form):
    title = forms.CharField()
    file_name = ResumableFileField(upload_url=reverse_lazy('upload'), chunks_dir="chuncks")
    section = forms.ModelChoiceField(queryset=Section.objects.order_by("title"), required=False)
