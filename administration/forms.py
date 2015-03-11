from django import forms
from django.contrib.auth.models import User

from sections.models import Section
from video.models import Video


class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    state = forms.BooleanField(required=False)


class VideoForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.all(), required=False)

    class Meta:
        model = Video
        fields = ['title', 'film_name', 'realisation', 'production', 'photo_direction', 'observations']


class FormUser(forms.ModelForm):
    password = forms.CharField(required=False)

    class Meta:
        model=User
        fields=['username', 'is_staff', 'first_name', 'last_name', 'email']
