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

        send_mail(
              u'Nouvelle vidéo "%s" dans la section "%s"' % (video.file_name, section.title),
              Template(EMAIL_TEMPLATE).render(Context(context)),
              'noreply@play.saya.fr',
              section.notification_email.split(","),
              html_message=Template(EMAIL_TEMPLATE_HTML).render(Context(context)),
              fail_silently=False
        )


EMAIL_TEMPLATE = u"""\
Bonjour,

Nous avons le plaisir de vous annoncer la mise en ligne sur Saya Play du
fichier suivant :

{{ section }} / {{ video }}
Lien de visionnage : {{ settings.BASE_URL }}{% url 'user_video_detail' video.pk %}

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
--Apple-Mail=_667BA9FF-430E-43BE-BFCF-6AC4365A374F
Content-Transfer-Encoding: quoted-printable
Content-Type: text/html;
	charset=utf-8

<html><head><meta http-equiv=3D"Content-Type" content=3D"text/html =
charset=3Dutf-8"></head><body style=3D"word-wrap: break-word; =
-webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" =
class=3D""><span style=3D"background-color: rgb(255, 255, 255);" =
class=3D"">Bonjour,</span><br style=3D"background-color: rgb(255, 255, =
255);" class=3D""><br style=3D"background-color: rgb(255, 255, 255);" =
class=3D""><div class=3D"rcmBody" style=3D"background-color: rgb(255, =
255, 255);"><div class=3D"">Nous avons le plaisir de vous annoncer la =
mise en ligne sur <u class=3D""><font color=3D"#0433ff" class=3D"">Saya =
Play</font></u>&nbsp;du fichier suivant :</div><div class=3D""><br =
class=3D""></div><div class=3D""><b class=3D""><br =
class=3D""></b></div><div class=3D""><b class=3D"">{{ section }}/{{ video }}
</b></div><div class=3D"">Lien de visionnage :&nbsp;<a =
class=3D"moz-txt-link-freetext" =
href=3D"{{ settings.BASE_URL }}{% url 'user_video_detail' video.pk %}">{{ settings.BASE_URL }}{% url 'user_video_detail' video.pk %}</a>=
</div><div class=3D""><br class=3D""></div><div class=3D""><br =
class=3D""></div><div class=3D"">Cordialement,<br class=3D""></div><div =
class=3D"">l'=C3=A9quipe Saya</div><div class=3D""><p class=3D""><em =
class=3D""><strong class=3D"">Article 226-15 :&nbsp;Le fait, commis de =
mauvaise foi, d'ouvrir, de supprimer, de retarder ou de d=C3=A9tourner =
des correspondances arriv=C3=A9es ou non =C3=A0 destination et =
adress=C3=A9es =C3=A0 des tiers, ou d'en prendre frauduleusement =
connaissance, est puni d'un an d'emprisonnement et de 45000 euros =
d'amende.</strong></em></p><p class=3D""><em class=3D""><strong =
class=3D"">Est puni des m=C3=AAmes peines le fait, commis de mauvaise =
foi, d'intercepter, de d=C3=A9tourner, d'utiliser ou de divulguer des =
correspondances =C3=A9mises, transmises ou re=C3=A7ues par la voie des =
t=C3=A9l=C3=A9communications ou de proc=C3=A9der =C3=A0 l'installation =
d'appareils con=C3=A7us pour r=C3=A9aliser de telles =
interceptions.</strong></em></p></div></div><div class=3D""><span =
style=3D"color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; =
font-style: normal; font-variant: normal; font-weight: normal; =
letter-spacing: normal; line-height: normal; orphans: auto; text-align: =
start; text-indent: 0px; text-transform: none; white-space: normal; =
widows: auto; word-spacing: 0px; -webkit-text-stroke-width: =
0px;"><span><span><span><span><img height=3D"100" width=3D"157" =
apple-inline=3D"yes" id=3D"523D1ADE-3491-40AC-A845-686F480AD662" =
apple-width=3D"yes" apple-height=3D"yes" =
src=3D"cid:E22A44A4-92B6-4BCB-97F9-A16D4445BAC0@local.saya.fr" =
class=3D""></span><br class=3D"Apple-interchange-newline" style=3D"color: =
rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: =
normal; font-variant: normal; font-weight: normal; letter-spacing: =
normal; line-height: normal; orphans: auto; text-align: start; =
text-indent: 0px; text-transform: none; white-space: normal; widows: =
auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;"><br =
style=3D"color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; =
font-style: normal; font-variant: normal; font-weight: normal; =
letter-spacing: normal; line-height: normal; orphans: auto; text-align: =
start; text-indent: 0px; text-transform: none; white-space: normal; =
widows: auto; word-spacing: 0px; -webkit-text-stroke-width: 0px;" =
class=3D""><div style=3D"color: rgb(0, 0, 0); font-family: Helvetica; =
font-size: 12px; font-style: normal; font-variant: normal; font-weight: =
normal; letter-spacing: normal; line-height: normal; orphans: auto; =
text-align: start; text-indent: 0px; text-transform: none; white-space: =
normal; widows: auto; word-spacing: 0px; -webkit-text-stroke-width: =
0px;" class=3D""><span style=3D"color: rgb(0, 0, 0); font-family: =
Helvetica; font-size: 12px; font-style: normal; font-variant: normal; =
font-weight: normal; letter-spacing: normal; line-height: normal; =
orphans: auto; text-align: start; text-indent: 0px; text-transform: =
none; white-space: normal; widows: auto; word-spacing: 0px; =
-webkit-text-stroke-width: 0px;"><span><div style=3D" font-family: =
Calibri, sans-serif;" class=3D""><span style=3D"font-family: Helvetica; =
font-size: 12px;" class=3D"">SAYA</span></div><div style=3D"font-size: =
medium; font-family: Calibri, sans-serif;" class=3D""><span =
style=3D"font-family: Helvetica; font-size: 12px;" class=3D"">32 rue des =
Je=C3=BBneurs - 75002 Paris</span></div><div style=3D" font-family: =
Calibri, sans-serif;" class=3D""><span style=3D"font-family: Helvetica; =
font-size: 12px;" class=3D"">Tel : +33 (0)1 42 21 10 58</span></div><div =
style=3D"font-size: medium; font-family: Calibri, sans-serif;" =
class=3D""><span style=3D"font-family: Helvetica; font-size: 12px;" =
class=3D""><a href=3D"mailto:florentin@saya.fr" =
class=3D"">florentin@saya.fr</a></span></div><div style=3D" font-family: =
Calibri, sans-serif;" class=3D""><span style=3D"font-family: Helvetica; =
font-size: 12px;" class=3D""><a href=3D"http://www.saya.fr" =
class=3D"">www.saya.fr</a></span></div></span></span></div><br =
class=3D"Apple-interchange-newline" style=3D"color: rgb(0, 0, 0); =
font-family: Helvetica; font-size: 12px; font-style: normal; =
font-variant: normal; font-weight: normal; letter-spacing: normal; =
line-height: normal; orphans: auto; text-align: start; text-indent: 0px; =
text-transform: none; white-space: normal; widows: auto; word-spacing: =
0px; -webkit-text-stroke-width: 0px;"><br =
class=3D""></span></span></span></span></div></body></html>=

--Apple-Mail=_667BA9FF-430E-43BE-BFCF-6AC4365A374F
Content-Transfer-Encoding: base64
Content-Disposition: inline;
	filename=Logo_Saya_2014_mail.png
Content-Type: image/png;
	name="Logo_Saya_2014_mail.png"
Content-Id: <E22A44A4-92B6-4BCB-97F9-A16D4445BAC0@local.saya.fr>

iVBORw0KGgoAAAANSUhEUgAAAJ0AAABkCAIAAAAT2aVQAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJ
bWFnZVJlYWR5ccllPAAAAyRpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdp
bj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6
eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0
NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJo
dHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlw
dGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAv
IiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RS
ZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpD
cmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoTWFjaW50b3NoKSIgeG1wTU06SW5zdGFu
Y2VJRD0ieG1wLmlpZDpBMzZBMjYwMzUyRjcxMUU0OTQ1NThEQ0IwM0U0QTIyMiIgeG1wTU06RG9j
dW1lbnRJRD0ieG1wLmRpZDpBMzZBMjYwNDUyRjcxMUU0OTQ1NThEQ0IwM0U0QTIyMiI+IDx4bXBN
TTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOkEzNkEyNjAxNTJGNzExRTQ5
NDU1OERDQjAzRTRBMjIyIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkEzNkEyNjAyNTJGNzEx
RTQ5NDU1OERDQjAzRTRBMjIyIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4
bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+g2QjLwAAKZZJREFUeNrsfQm0JFWZ5v0jM9++1ltq
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
39Dwvr6BHz35rPAqwRV0cdze2jxegNnBke89+uQfvOuMQqlYScSkHIPZ8sXvPvtnv37muq9/K1H2
brnuU2edfNyDv3xS1JcMj0t0vuHxCevjl9vc3JXnv/Nrt9116x0/aOho/eZfX9PYUG9xzbSW16kV
MgYZrw57ajZRqXz+vi1/fd+WtrpiR0Oxq7Gup7k+UZp6W5t62lpS1amttaOtpa2lubW5uamxIf3X
kOpNAPDa3zFiqjfNlqdnpienpicmp8YmJ0fGJgbHxgfHJ/vHJvrGp/onpgemygPT5ZGZubFyRlmp
bVrN+Cc6jpCUIMtz7znj1MvPOnX3voNHr1v932/7wezkdAqbNlfecexR33v48b6R0WQofrz5qfNO
PeHBRx5PWDApw4nHE5bGkrWw0Nx81OqV37z7nkNjY6K/f8uLO87aeJIOC6V2WrzmvA/sHRiKCgXd
4cIp+wKWHamzHdi7ArxCOX0wog7eiJuk5CPKvCnIdM5kJ3NFFKw7NxZ1BWgsJrYNNBaiplJq4TQU
C40lZeTUR6IhUZIjIVu4FzNHX0GaBFLTiVMBVEkelbRPeRnFTHlutoozc5WZajwzV52uJA+cyp7T
I9W4XEXt9FAJFImFI5SFk6ib1dTMzQwoiaAqbDUPEcsuksn5a5Z2L+tsf+Vg34H9fYk1ltGxNJex
s7V5ZHxCWk2lYtTa2DA0MqZ7osue5ZAcHBkfpxdPhqejuWlodDQ1BuO4uVrZ+fA9Szo7LR+uKxaA
ejEwPyiNDnPFmt5qQeuZSGwiUOuWGfGpHyCz2xIwKpjNAATpMkwnXDmOypV4rFpIsxJms0ysSHZn
SE7IOh7DnDzTuJcx2IdABVKNI0I/x0K2W8qg0g3Lq6mDImu/a/CTV1AHSRKMT/xWX9y579DORBNO
0Eh0XWTt2oYlitlIzM1VhmbG0tPI9ZJpOJKcU6CepmRG4dDwCBRSN0VCCfF0OeFhhA8DNCTTB2ok
5PDSA7PHwCV5WhxIN+oo0zIZvjphMiyUEdE4uWNRBYxkrJQVBdtCUuXUV7EpMH59Yb2qZFjV3Nc9
WrLEklhViaMlDsFyg0l83S2WsnkWyOvXUgU64R4p+fo9QaJImHqb1JMSufXzkHIe32qB1A5WvymR
TaZrscK12VhLuXk4GMppJn0wqCMbaIAilL1jylSY15PnHdFkPxMLQZUspuNh6ARF/Uxc1JFOdKrn
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
--Apple-Mail=_667BA9FF-430E-43BE-BFCF-6AC4365A374F--
"""
