from django import template

from sections.models import Permission


register = template.Library()


@register.simple_tag
def is_user_have_access(section, user):
    if Permission.objects.filter(user=user, section=section).exists():
        return "true"
    return "false"


@register.simple_tag
def is_group_have_access(section, group):
    if section in group.get_permissions():
        return "true"
    return "false"


@register.simple_tag
def level_to_heading_number(level_number):
    return 2 + level_number
