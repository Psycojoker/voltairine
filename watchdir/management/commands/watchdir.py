import os
import sys
import time
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from sections.models import Section, VideoSection
from video.models import Video


class Command(BaseCommand):
    help = 'Launch watchdir daemon'

    def handle(self, *args, **options):
        self.base_path = os.path.join(os.curdir, "ftp")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        try:
            while True:
                videos = {}
                sections_map = {}

                sections_map = self.update_directories_hierarchy()

                videos = self.parse_all_videos(videos, sections_map)

                self.handle_videos(videos)
                time.sleep(3)

        except KeyboardInterrupt:
            sys.exit(0)

    def update_directories_hierarchy(self):
        def _recursivly_generate_directories(base, section, childrens):
            path = os.path.join(base, section.title)
            partage = os.path.join(path, "PARTAGE")

            sections_map[path] = section
            if not os.path.exists(path):
                os.makedirs(path)

            if not os.path.exists(partage):
                os.makedirs(partage)

            for sub_section, sub_childrens in childrens:
                _recursivly_generate_directories(path, sub_section, sub_childrens)

        sections_map = {}
        for section, childrens in Section.objects.all().as_python_tree():
            _recursivly_generate_directories(self.base_path, section, childrens)

        return sections_map

    def parse_all_videos(self, videos, sections_map):
        def handle_dir(_, dirname, names):
            for name in names:
                file_path = os.path.join(dirname, name)

                if not os.path.isfile(file_path) or not file_path.lower().endswith(".mp4"):
                    continue

                # TODO partage/Vantage

                videos[file_path] = {
                    "name": name,
                    "section": sections_map[dirname],
                    "last_modification_time": time.time() - os.path.getmtime(file_path),
                    "send_notification": False,  # TODO Vantage
                }

        # TODO parse sections_map instead
        os.path.walk(self.base_path, handle_dir, None)
        return videos

    def handle_videos(self, videos):
        for video_path, informations in videos.items():
            if informations["last_modification_time"] < 4:
                continue

            # TODO unique filename, clean filename (see upload_video/views.py#56)
            file_name = informations["name"]
            section = informations["section"]

            print "Detecting new video '%s', loading it into saya into the section '%s'" % (video_path, section)

            shutil.move(
                src=video_path,
                dst=os.path.join(settings.MEDIA_ROOT, "videos", file_name)
            )

            video = Video.objects.create(
                title=informations["name"][:-len(".mp4")],
                file_name=file_name,
            )

            VideoSection.objects.create(
                video=video,
                section=section,
            )
