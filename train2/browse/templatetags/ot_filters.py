import json

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
    return dt.astimezone(ISRAEL_TIMEZONE).strftime('%H:%M:%S')

@register.filter
def delay(secs):
    if secs is None:
        return '----'
    return secs

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


@register.filter
def uid(obj):
    if hasattr(obj,'get_absolute_url'):
        return mark_safe('<a href="{0}">{1}</a>'.format(obj.get_absolute_url(),obj.id))
    return obj.id


@register.filter
def route_ids_json(objs):
    route_ids = [obj.id for obj in objs]
    return json.dumps(route_ids)


@register.simple_tag
def stop_time_span(dt):
    if not dt:
        return '----'
    dt_il = dt.astimezone(ISRAEL_TIMEZONE)
    return mark_safe('<span title="{0}">{1}</span>').format(
        dt_il.isoformat(),
        dt_il.strftime('%H:%M:%S'))