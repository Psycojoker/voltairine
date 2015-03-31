from django import forms
from django.contrib.auth.models import User
from mptt.forms import TreeNodeChoiceField
from permissions_groups.models import Group

from sections.models import Section
from video.models import Video


class UserPermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    section = TreeNodeChoiceField(queryset=Section.objects.all())
    state = forms.BooleanField(required=False)


class GroupPermissionForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    section = TreeNodeChoiceField(queryset=Section.objects.all())
    state = forms.BooleanField(required=False)


class VideoForm(forms.ModelForm):
    section = TreeNodeChoiceField(queryset=Section.objects.all(), required=False)

    class Meta:
        model = Video
        fields = ['title', 'film_name', 'realisation', 'production', 'photo_direction', 'lto_archive_number', 'observations']


class FormUser(forms.ModelForm):
    password = forms.CharField(required=False)

    class Meta:
        model=User
        fields=['username', 'is_staff', 'first_name', 'last_name', 'email']


class FormUserForGroupAdmin(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None)
    password = forms.CharField(required=False)

    class Meta:
        model=User
        fields=['username', 'first_name', 'last_name', 'email']
