from django import forms
from django.core.urlresolvers import reverse_lazy

from resumable.fields import ResumableFileField

from sections.models import SubSubSection


class ResumableForm(forms.Form):
    title = forms.CharField()
    file_name = ResumableFileField(upload_url=reverse_lazy('upload'), chunks_dir="chuncks")
    subsubsection = forms.ModelChoiceField(queryset=SubSubSection.objects.filter(subsection__section="1"), required=False)
