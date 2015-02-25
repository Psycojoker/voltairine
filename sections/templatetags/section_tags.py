from django import template

from sections.models import Permission


register = template.Library()


@register.simple_tag
def is_user_have_access(subsubsection, user):
    if Permission.objects.filter(user=user, subsubsection=subsubsection).exists():
        return "true"
    return "false"
