from django import forms
from django.contrib.auth.models import User

from sections.models import SubSubSection


class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    subsubsection = forms.ModelChoiceField(queryset=SubSubSection.objects.all())
    state = forms.BooleanField(required=False)
