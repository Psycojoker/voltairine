from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from video.models import Video


@login_required
def dashboard(request):
    return render(request, 'regular_users_interface/dashboard.haml', {
        "video_list": Video.objects.filter(videosection__subsubsection__permission__user=request.user),
    })
