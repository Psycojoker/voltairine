from django.shortcuts import render


def dashboard(request):
    return render(request, 'regular_users_interface/dashboard.haml', {})
