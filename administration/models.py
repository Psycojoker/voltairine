from django.contrib.auth.models import User


def render_user(self):
    if self.first_name and self.last_name:
        return "%s %s (%s) <%s>%s" % (self.first_name, self.last_name, self.username, self.email, (" - administrateur" if self.is_staff else ""))

    return "%s <%s>%s" % (self.username, self.email, (" - administrateur" if self.is_staff else ""))


User.__unicode__ = render_user
