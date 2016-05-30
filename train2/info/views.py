from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, FormView, View
from django import forms

from functools import lru_cache

import data.models
import requests


class RoutesForm(forms.Form):
    route_id = forms.IntegerField()
    old_or_new = forms.ChoiceField(label='convert from',
                                   choices=(
                                       ('new', 'new site (next.otrain.org'),
                                       ('old', 'old site (otrain.org)')
                                       ))



@lru_cache()
def get_old_routes():
    all_routes = []
    url = 'http://otrain.org/api/v1/routes/'
    while url:
        resp = requests.get(url).json()
        all_routes += resp['results']
        url = resp['next']
        size = resp['count']
    assert len(all_routes) == size
    result = [{
                  'id': route['id'],
                  'stop_ids': [s['gtfs_stop_id'] for s in route['stops']]
              } for route in all_routes]
    assert len(result) == size
    return result


def find_old_route_by_stop_ids(stop_ids):
    old_routes = get_old_routes()
    for old_route in old_routes:
        if old_route['stop_ids'] == stop_ids:
            return old_route
    return None


def find_old_route_by_id(route_id):
    old_routes = get_old_routes()
    for old_route in old_routes:
        if old_route['id'] == route_id:
            return old_route
    return None


class RoutesView(FormView):
    form_class = RoutesForm
    template_name = 'info/routes.html'

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        route_id = self.request.GET.get('route_id')
        is_new = self.request.GET.get('is_new')
        if route_id is not None:
            route_id = int(route_id)
            is_new = int(is_new)
            if is_new:
                new_route_id, old_route_id = route_id, self.new_to_old(route_id)
            else:
                new_route_id, old_route_id = self.old_to_new(route_id), route_id
            d['has_result'] = True
            d['old_route_id'] = old_route_id
            d['new_route_id'] = new_route_id
            d['stops'] = data.models.Route.objects.get(id=new_route_id).get_stops()
        return d

    def new_to_old(self, route_id):
        new_route = data.models.Route.objects.get(id=route_id)
        stop_ids = new_route.stop_ids
        old_route = find_old_route_by_stop_ids(stop_ids)
        if old_route:
            return old_route['id']
        return None

    def old_to_new(self, route_id):
        old_route = find_old_route_by_id(route_id)
        assert old_route is not None, 'Illegal old_route {}'.format(route_id)
        try:
            new_route = data.models.Route.objects.get(stop_ids=old_route['stop_ids'])
            return new_route.id
        except data.models.Route.DoesNotExist:
            return None

    def form_valid(self, form):
        is_new = form.cleaned_data['old_or_new'] == 'new'
        route_id = form.cleaned_data['route_id']
        self.success_url = '{}?is_new={}&route_id={}'.format(reverse('info:routes'),
                                                             1 if is_new else 0,
                                                             route_id)
        return super().form_valid(form)


class HeatView(View):
    @method_decorator(never_cache)
    def get(self, request):
        from data.analysis.heatmap_utils import run
        html = run()
        return HttpResponse(html)

