# encoding: utf-8

import os
import grp
import sys
import time
import shutil
import logging
from email.mime.image import MIMEImage

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
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

                self.remove_unused_directories(sections_map)

                videos = self.parse_all_videos(videos, sections_map)

                self.handle_videos(videos)
                time.sleep(3)

        except KeyboardInterrupt:
            sys.exit(0)

    def update_directories_hierarchy(self):
        def _recursivly_generate_directories(base, section, childrens):
            path = os.path.join(base, section.title.encode("Utf-8"))

            sections_map[path] = section
            if not os.path.exists(path):
                logger.info("Create new directory '%s' for section '%s'", path, section.title.encode("Utf-8"))
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
            _recursivly_generate_directories(self.base_path.encode("Utf-8"), section, childrens)

        return sections_map

    def remove_unused_directories(self, sections_map):
        used_paths = set(sections_map.keys())

        for path, files, _ in os.walk(self.base_path.encode("Utf-8")):
            if path == self.base_path:
                continue

            # remove unused directories that don't contains any files
            if path not in used_paths and not files:
                logger.info("Removed empty unused directory '%s' that don't map to any section", path)
                shutil.rmtree(path)
            elif path not in used_paths:
                logger.warning("Can't remove directory '%s' that don't map to any section because it contains the files '%s'", path, ", ".join(files))

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
        context = {
            "video": video,
            "section": section,
            "settings": settings,
        }

        message = EmailMultiAlternatives(
              u"[SAYA - Play] Mise en ligne : %s / %s" % (video.file_name, section.title),
              Template(EMAIL_TEMPLATE).render(Context(context)),
              'noreply@play.saya.fr',
              section.notification_email.split(","),
        )

        with open("logo_saya_mail.png", "rb") as f:
            logo_data = f.read()

        logo = MIMEImage(logo_data)
        logo.add_header('Content-ID', '<logo>')

        message.mixed_subtype = 'related'
        message.attach_alternative(Template(EMAIL_TEMPLATE_HTML).render(Context(context)), "text/html")
        message.attach(logo)
        message.send()


EMAIL_TEMPLATE = u"""\
Bonjour,

Nous avons le plaisir de vous annoncer la mise en ligne sur Saya Play du
fichier suivant :

{{ section }} / {{ video }}
Lien de visionnage : {{ settings.BASE_URL }}{% url 'administration_video_detail' video.pk %} <{{ settings.BASE_URL }}{% url 'administration_video_detail' video.pk %}>

Cordialement,
l'équipe Saya

Article 226-15 : Le fait, commis de mauvaise foi, d'ouvrir, de supprimer, de
retarder ou de détourner des correspondances arrivées ou non à destination et
adressées à des tiers, ou d'en prendre frauduleusement connaissance, est puni
d'un an d'emprisonnement et de 45000 euros d'amende.

Est puni des mêmes peines le fait, commis de mauvaise foi, d'intercepter, de
détourner, d'utiliser ou de divulguer des correspondances émises, transmises ou
reçues par la voie des télécommunications ou de procéder à l'installation
d'appareils conçus pour réaliser de telles interceptions.


-- 
SAYA
32 rue des Jeûneurs - 75002 Paris
Tel : +33 (0)1 42 21 10 58
florentin@saya.fr
www.saya.fr
"""


EMAIL_TEMPLATE_HTML = u"""\
<html>
<head>
<meta http-equiv="Content-Type" content="text/html charset=utf-8">
</head>
<body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">
<span style="background-color: rgb(255, 255, 255);" class="">
Bonjour,</span>
<br style="background-color: rgb(255, 255, 255);" class="">
<br style="background-color: rgb(255, 255, 255);" class="">
<div class="rcmBody" style="background-color: rgb(255, 255, 255);">
<div class="">
Nous avons le plaisir de vous annoncer la mise en ligne sur <u class="">
<font color="#0433ff" class="">
Saya Play</font>
</u>
&nbsp;du fichier suivant :</div>
<div class="">
<br class="">
</div>
<div class="">
<b class="">
<br class="">
</b>
</div>
<div class="">
<b class="">
{{ section }} / {{ video }}
</div>
<div class="">
Lien de visionnage :&nbsp;<a class="moz-txt-link-freetext" href="{{ settings.BASE_URL }}{% url 'administration_video_detail' video.pk %}">
{{ settings.BASE_URL }}{% url 'administration_video_detail' video.pk %}</a>
</div>
<div class="">
<br class="">
</div>
<div class="">
<br class="">
</div>
<div class="">
Cordialement,<br class="">
</div>
<div class="">
l'équipe Saya</div>
<div class="">
<p class="">
<em class="">
<strong class="">
Article 226-15 :&nbsp;Le fait, commis de mauvaise foi, d'ouvrir, de supprimer, de retarder ou de détourner des correspondances arrivées ou non à destination et adressées à des tiers, ou d'en prendre frauduleusement connaissance, est puni d'un an d'emprisonnement et de 45000 euros d'amende.</strong>
</em>
</p>
<p class="">
<em class="">
<strong class="">
Est puni des mêmes peines le fait, commis de mauvaise foi, d'intercepter, de détourner, d'utiliser ou de divulguer des correspondances émises, transmises ou reçues par la voie des télécommunications ou de procéder à l'installation d'appareils conçus pour réaliser de telles interceptions.</strong>
</em>
</p>
</div>
</div>
<div class="">
<span style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;">
<span>
<span>
<span>
<span>
<img height="100" width="157" apple-inline="yes" id="logo" apple-width="yes" apple-height="yes" src="cid:logo" class="">
</span>
<br class="Apple-interchange-newline" style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;">
<br style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;" class="">
<div style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;" class="">
<span style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;">
<span>
<div style=" font-family: Calibri, sans-serif;" class="">
<span style="font-family: Helvetica; font-size: 12px;" class="">
SAYA</span>
</div>
<div style="font-size: medium; font-family: Calibri, sans-serif;" class="">
<span style="font-family: Helvetica; font-size: 12px;" class="">
32 rue des Jeûneurs - 75002 Paris</span>
</div>
<div style=" font-family: Calibri, sans-serif;" class="">
<span style="font-family: Helvetica; font-size: 12px;" class="">
Tel : +33 (0)1 42 21 10 58</span>
</div>
<div style="font-size: medium; font-family: Calibri, sans-serif;" class="">
<span style="font-family: Helvetica; font-size: 12px;" class="">
<a href="mailto:florentin@saya.fr" class="">
florentin@saya.fr</a>
</span>
</div>
<div style=" font-family: Calibri, sans-serif;" class="">
<span style="font-family: Helvetica; font-size: 12px;" class="">
<a href="http://www.saya.fr" class="">
www.saya.fr</a>
</span>
</div>
</span>
</span>
</div>
<br class="Apple-interchange-newline" style="color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; line-height: normal; orphans: auto; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;">
<br class="">
</span>
</span>
</span>
</span>
</div>
</body>
</html>
"""
