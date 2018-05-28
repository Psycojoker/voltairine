# encoding: utf-8

from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, NumericPasswordValidator


class UserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def get_help_text(self):
        return "Veillez à ce que votre mot de passe ne contienne pas d’informations personnelles."


class NumericPasswordValidator(NumericPasswordValidator):
    def get_help_text(self):
        return "Votre mot de passe ne doit pas être entièrement numérique."
