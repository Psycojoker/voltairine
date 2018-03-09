# encoding: utf-8

import os
import grp
import sys
import time
import shutil
import logging

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.db import transaction

from sections.models import Section, VideoSection
from video.models import Video
from upload_video.utils import ensure_file_name_is_unique, clean_file_name

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Launch watchdir daemon'

    def handle(self, *args, **options):
        self.base_path = os.path.join(os.curdir, "ftp")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        logger.info("Started watchdir daemon")
        self.has_seen_chgrp_error = False

        self.saya_watchdir_group_id = None
        try:
            self.saya_watchdir_group_id = grp.getgrnam("saya_watchdir").gr_gid
        except KeyError:
            logger.warning("The group 'saya_watchdir' doesn't exist on the system, it won't be possible to set it on the directories.")

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
            path = os.path.join(base, section.title).encode("Utf-8")

            sections_map[path] = section
            if not os.path.exists(path):
                os.makedirs(path)

            os.chmod(path, 0775)
            if self.saya_watchdir_group_id is not None:
                try:
                    os.chown(path, -1, self.saya_watchdir_group_id)

                except OSError, e:
                    if not self.has_seen_chgrp_error:
                        logger.warning("I can't chgrp '%s' because of '%s'", path, e)
                        logger.warning("Check that this process is launched by a user in the 'saya_watchdir' group (check with the 'groups' command) and DON'T FORGET TO RELOG after adding it to it.")
                        self.has_seen_chgrp_error = True

            for sub_section, sub_childrens in childrens:
                _recursivly_generate_directories(path, sub_section, sub_childrens)

        sections_map = {}
        for section, childrens in Section.objects.all().as_python_tree():
            _recursivly_generate_directories(self.base_path, section, childrens)

        return sections_map

    def parse_all_videos(self, videos, sections_map):
        for path in sections_map.keys():
            for name in os.listdir(path):
                file_path = os.path.join(path, name)

                if not os.path.isfile(file_path) or not file_path.lower().endswith(".mp4"):
                    continue

                videos[file_path] = {
                    "name": name,
                    "section": sections_map[path],
                    "last_modification_time": time.time() - os.path.getmtime(file_path),
                    "send_notification": False,
                }

        return videos

    def handle_videos(self, videos):
        for video_path, informations in videos.items():
            if informations["last_modification_time"] < 4:
                continue

            section = informations["section"]
            destination = os.path.join(settings.MEDIA_ROOT, "videos")
            file_name = informations["name"]

            file_name = clean_file_name(file_name)
            file_name = ensure_file_name_is_unique(destination, file_name)

            logger.info("Detecting new video '%s', loading it into saya into the section '%s' as '%s'" , video_path, section, file_name)

            try:
                with transaction.atomic():
                    video = Video.objects.create(
                        title=informations["name"][:-len(".mp4")],
                        file_name=file_name,
                    )

                    VideoSection.objects.create(
                        video=video,
                        section=section,
                    )

                    shutil.move(
                        src=video_path,
                        dst=os.path.join(destination, file_name),
                    )
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(e)
                logger.error("Failed to upload video '%s'", video_path)
                continue

            if section.notification_email:
                try:
                    self.send_notification_email(section, video)
                    logger.info("Sent notification email to '%s' about '%s' in '%s'", section.notification_email, video.file_name, section.title)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    logger.error(e)

    def send_notification_email(self, section, video):
        send_mail(
              u'Nouvelle vidéo "%s" dans la section "%s"' % (video.file_name, section.title),
              Template(EMAIL_TEMPLATE).render(Context({"video": video, "section": section, "settings": settings})),
              'noreply@play.saya.fr',
              section.notification_email.split(","),
              fail_silently=False
        )


EMAIL_TEMPLATE = u"""\
Bonjour,

Une nouvelle vidéo '{{ video }}' vient d'être mise en ligne dans la section '{{ section }}'.
Vous pouvez la visionner à cette adresse : {{ settings.BASE_URL }}{% url 'user_video_detail' video.pk %}

Bien à vous,
"""
