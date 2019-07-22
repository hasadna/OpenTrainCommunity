from django import template

register = template.Library()


@register.filter
def strip_seconds(hms):
    try:
        h,m,s = hms.split(":")
        return f'{h}:{m}'
    except ValueError:
        return hms
