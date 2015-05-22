from django import forms


class ForgottenPasswordForm(forms.Form):
    username = forms.CharField(label="Identifiant")
    email = forms.EmailField(label="Votre adresse e-mail")
