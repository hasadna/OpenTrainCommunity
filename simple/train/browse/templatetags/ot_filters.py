from django import template
from django.template.defaultfilters import mark_safe
from django.conf import settings
register = template.Library()

import pytz
ISRAEL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


@register.filter
def stop_time(dt):
    if not dt:
        return '----'
    return dt.astimezone(ISRAEL_TIMEZONE).strftime('%H:%M')

@register.filter
def heb_stop_name(stop_id):
    import data.services
    return data.services.get_heb_stop_name(stop_id)

@register.filter
def modelname(obj):
    return obj.__class__.__name__.lower()

@register.filter
def secondsOrNA(d):
    if d is None:
        return '--'
    return '%.2f' % d


@register.filter
def u(obj):
    if hasattr(obj,'get_absolute_url'):
        return mark_safe('<a href="{0}">{1}</a>'.format(obj.get_absolute_url(),obj))
    return obj




