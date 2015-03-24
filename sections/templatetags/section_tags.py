from django import template

from sections.models import Permission
from permissions_groups.models import Group


register = template.Library()


@register.simple_tag
def is_user_have_access(section, user):
    if Permission.objects.filter(user=user, section=section).exists():
        return "true"
    return "false"


@register.simple_tag
def is_group_have_access(section, group):
    if Group.objects.filter(pk=group.pk, permissions=section).exists():
        return "true"
    return "false"


@register.simple_tag(takes_context=True)
def increment(context, variable_name):
    context.dicts[2][variable_name] += 1
    return ""


@register.simple_tag(takes_context=True)
def decrement(context, variable_name):
    context.dicts[2][variable_name] -= 1
    return ""
