from django import forms

from django.contrib.auth.models import User


class ForgottenPasswordForm(forms.Form):
    username = forms.CharField(label="Identifiant")
    email = forms.EmailField(label="Votre adresse e-mail")

    def clean_username(self):
        username = self.cleaned_data['username']

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Cet utilisateur n'existe pas")

        return username
