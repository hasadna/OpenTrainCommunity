from django import template
from django.conf import settings
register = template.Library()

import pytz
ISRAEL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


@register.filter(name='stop_time')
def stop_time(dt):
    if not dt:
        return '----'
    return dt.astimezone(ISRAEL_TIMEZONE).strftime('%H:%M')

@register.filter(name="heb_stop_name")
def heb_stop_name(stop_id):
    import data.services
    return data.services.get_heb_stop_name(stop_id)

@register.filter(name="modelname")
def modelname(obj):
    return obj.__class__.__name__.lower()

@register.filter(name="secondsOrNA")
def secondsOrNA(d):
    if d is None:
        return '--'
    return d



