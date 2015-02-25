from django import template

register = template.Library()


@register.simple_tag
def is_user_have_access(subsubsection, user):
    return "true"
