import functools
from django import forms
from django.utils.translation import ugettext as _
import data.services
from data.models import Route


@functools.lru_cache()
def get_all_routes():
    import data.models
    routes = list(Route.objects.all())
    keys = set()
    for route in routes:
        keys.add((route.stop_ids[0],route.stop_ids[-1]))
    choices = [(0,'------------')]
    for key in keys:
        s1 = data.services.get_stop(key[0])['heb_stop_names'][0]
        s2 = data.services.get_stop(key[1])['heb_stop_names'][0]
        choices.append(('{0},{1}'.format(*key),'{0} {1} {2}'.format(s1,_('to'),s2)))
    choices.sort(key=lambda x: x[1])
    return choices


@functools.lru_cache()
def get_all_stops():
    result = [(0,'------------')]
    stop_ids = set(r.stop_ids[0] for r in Route.objects.all())
    stops = data.services.get_stops(stop_ids)
    result += [(s['stop_id'],s['heb_stop_names'][0]) for s in stops]
    result.sort(key=lambda x:x[1])
    return result


class FilterStopsForm(forms.Form):
    route = forms.ChoiceField(choices=get_all_routes(), label=_('route'), required=False)
    source = forms.ChoiceField(choices=get_all_stops(),label=_('source'),required=False)
    min_stops = forms.IntegerField(min_value=0,label=_('min stops'),required=False)

