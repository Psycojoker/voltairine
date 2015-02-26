from django.shortcuts import render

from video.models import Video


def dashboard(request):
    return render(request, 'regular_users_interface/dashboard.haml', {
        Video.objects.filter(videosection__subsubsection__permission__user=request.user),
    })
