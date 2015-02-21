from django.contrib.auth.views import login as base_login


def login(request):
    return base_login(request, template_name="registration/login.haml")
