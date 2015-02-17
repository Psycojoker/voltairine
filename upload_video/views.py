from django.shortcuts import render


def upload_video(request):
    return render(request, "upload/upload.haml", {})
