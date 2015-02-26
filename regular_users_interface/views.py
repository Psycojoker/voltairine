from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from sections.models import SubSection


@login_required
def dashboard(request):
    return render(request, 'regular_users_interface/dashboard.haml', {
        "subsection_list": SubSection.objects.filter(subsubsection__permission__user=request.user).distinct(),
    })
