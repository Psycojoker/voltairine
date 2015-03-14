from django import template

from sections.models import Permission


register = template.Library()


@register.simple_tag
def is_user_have_access(section, user):
    if Permission.objects.filter(user=user, section=section).exists():
        return "true"
    return "false"
