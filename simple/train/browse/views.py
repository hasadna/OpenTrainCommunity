import os.path

import functools
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import FormMixin

from data.models import Route, Service, Trip, Sample
from . import forms


class BrowseMixin:
    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['breadcrumbs'] = self.get_breadcrumbs()
        assert isinstance(d['breadcrumbs'], list)
        for bc in d['breadcrumbs']:
            assert isinstance(bc, tuple)
            assert len(bc) == 2
        return d

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def dispatch(self, request, *args, **kwargs):
        self.pre_dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def pre_dispatch(self, request, *args, **kwargs):
        pass


class BrowseRoutes(FormMixin, ListView):
    model = Route
    template_name = 'browse/browse_routes.html'
    form_class = forms.FilterStopsForm
    breadcrumbs = [
        (_('Routes'), reverse_lazy('browse:routes'))
    ]

    def get(self, request):
        self.form = self.get_form_class()(request.GET)
        return super().get(request)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.form.is_valid():
            route = self.form.cleaned_data['route']
            source = self.form.cleaned_data['source']
            if route and route == '0':
                route = None
            if source and source == '0':
                source = None
            if route and source:
                self.form.add_error(None,_('Select only one of source and route'))
            if route or source:
                if route:
                    self.is_route = True
                    start_stop_id, end_stop_id = route.split(',')
                    start_stop_id = int(start_stop_id)
                    end_stop_id = int(end_stop_id)
                if source:
                    start_stop_id = int(source)
                    end_stop_id = None
                self.start_stop_id = start_stop_id
                self.end_stop_id = end_stop_id
                all_routes = list(qs)
                routes = []
                for r in all_routes:
                    if r.stop_ids[0] == start_stop_id and (r.stop_ids[-1] == end_stop_id or end_stop_id is None):
                        routes.append(r)
                return routes

        return qs.none()

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=self.form, **kwargs)

class BrowseCompareRoutes(ListView):
    template_name = 'browse/compare_routes.html'
    model = Route

    def get_queryset(self):
        qs = super().get_queryset()
        start_stop_id = int(self.request.GET['start_stop_id'])
        end_stop_id = int(self.request.GET['end_stop_id'])
        all_routes = list(qs)
        routes = []
        for r in all_routes:
            if r.stop_ids[0] == start_stop_id and r.stop_ids[-1] == end_stop_id:
                routes.append(r)
        self.routes = routes
        self.all_stop_ids = self.get_all_stops(routes)
        for r in routes:
            r.vector = tuple(s in r.stop_ids for s in self.all_stop_ids)
            binstr = ''.join(str(int(x)) for x in r.vector)
            r.checksum = int(binstr,2)


        routes.sort(key=lambda r:r.vector)
        checksums = [r.checksum for r in routes]
        for r in routes:
            r.checksum_index = checksums.index(r.checksum)



        return routes

    def get_all_stops(self, routes):
        all_stop_ids = set()
        for r in routes:
            all_stop_ids |= set(r.stop_ids)

        def cmp_stops(s1,s2):
            for r in routes:
                try:
                    idx1 = r.stop_ids.index(s1)
                    idx2 = r.stop_ids.index(s2)
                    if idx1 > idx2:
                        return 1
                    if idx1 < idx2:
                        return -1
                    return 0
                except ValueError:
                    pass
            return 0

        all_stop_ids = list(all_stop_ids)
        all_stop_ids.sort(key=functools.cmp_to_key(cmp_stops))
        return all_stop_ids

    def get_context_data(self, **kwargs):
        return super().get_context_data(all_stop_ids=self.all_stop_ids)







class BrowseRoute(BrowseMixin, DetailView):
    model = Route
    template_name = 'browse/browse_route.html'

    def get_breadcrumbs(self):
        route = self.get_object()
        return BrowseRoutes.breadcrumbs + [
            (route.get_short_name(), reverse_lazy('browse:route', kwargs={'pk': route.id}))
        ]


class BrowseService(BrowseMixin, DetailView):
    template_name = 'browse/browse_service.html'
    model = Service

    def get_breadcrumbs(self):
        service = self.get_object()
        route = service.route
        return BrowseRoutes.breadcrumbs + [
            (route.get_short_name(), reverse_lazy('browse:route', kwargs={'pk': route.id})),
            (service.get_short_name(), reverse_lazy('browse:service', kwargs={'pk': service.id})),
        ]


class BrowseTrip(BrowseMixin, DetailView):
    template_name = 'browse/browse_trip.html'
    model = Trip

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        trip = self.get_object()
        d['samples'] = list(trip.get_real_stop_samples())
        return d

    def get_breadcrumbs(self):
        trip = self.get_object()
        service = trip.service
        route = service.route

        return BrowseRoutes.breadcrumbs + [
            (route.get_short_name(), reverse_lazy('browse:route', kwargs={'pk': route.id})),
            (service.get_short_name(), reverse_lazy('browse:service', kwargs={'pk': service.id})),
            (trip.get_short_name(), reverse_lazy('browse:trip', kwargs={'pk': trip.id})),
        ]


class RawDateView(TemplateView):
    template_name = 'browse/browse_raw_data.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        OFFSET = 20
        filename = self.request.GET['file']
        lineno = int(self.request.GET['line'])
        sample_id = int(self.request.GET['sample_id'])
        sample = get_object_or_404(Sample, pk=sample_id)
        from_lineno = max(0, lineno - OFFSET)
        to_lineno = (lineno + OFFSET)
        cur_lineno = 1
        lines = []
        file_path = os.path.join(settings.TXT_FOLDER, filename)
        with open(file_path, encoding="windows-1255") as fh:
            for line in fh:
                if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                    lines.append({'lineno': cur_lineno,
                                  'line': line.strip().encode('utf-8', errors='ignore')})
                cur_lineno += 1
        ctx['lines'] = lines
        ctx['filename'] = filename
        ctx['lineno'] = lineno
        ctx['prev'] = sample.get_text_link(line=lineno - OFFSET * 2 - 1)
        ctx['next'] = sample.get_text_link(line=lineno + OFFSET * 2 - 1)
        return ctx
