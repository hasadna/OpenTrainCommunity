import json
import os.path

import functools

import datetime

import pytz
import xlrd
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import FormMixin

from data.models import Route, Trip, Sample, Stop
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


class BrowseRoutes(BrowseMixin, ListView):
    model = Route
    template_name = 'browse/browse_routes.html'
    # form_class = forms.FilterStopsForm
    breadcrumbs = [
        (_('Routes'), reverse_lazy('browse:routes'))
    ]

    # def get(self, request):
    #     self.form = self.get_form_class()(request.GET)
    #     return super().get(request)

    def get_queryset(self):
        qs = super().get_queryset()
        from_gtfs = int(self.request.GET.get('from', 0))
        to_gtfs = int(self.request.GET.get('to', 0))
        if not from_gtfs or not to_gtfs:
            qs = qs.none()
        else:
            min_stops = int(self.request.GET.get('min_stops', 0))
            route_ids = [r.id for r in qs if
                         r.stop_ids[0] == from_gtfs
                         and r.stop_ids[-1] == to_gtfs
                         and r.trips.count() >= min_stops
                         ]

            qs = qs.filter(id__in=route_ids)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['all_stops'] = sorted(list(Stop.objects.all()), key=lambda s: s.main_name)
        return ctx


class BrowseCompareRoutes(ListView):
    template_name = 'browse/compare_routes.html'
    model = Route

    def get_queryset(self):
        qs = super().get_queryset()
        route_ids = json.loads(self.request.GET['routes'])
        routes = list(Route.objects.filter(id__in=route_ids))
        self.all_stop_ids = self.get_all_stops(routes)
        for r in routes:
            r.vector = tuple(s in r.stop_ids for s in self.all_stop_ids)
            binstr = ''.join(str(int(x)) for x in r.vector)
            r.checksum = int(binstr, 2)

        routes.sort(key=lambda r: r.vector)
        checksums = [r.checksum for r in routes]
        for r in routes:
            r.checksum_index = checksums.index(r.checksum)
        return routes

    def get_all_stops(self, routes):
        all_stop_ids = set()
        for r in routes:
            all_stop_ids |= set(r.stop_ids)

        def cmp_stops(s1, s2):
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
        ext = os.path.splitext(filename)[1]
        assert ext in ['.txt', '.xlsx'], 'illegal ext = {0}, filename = {1}'.format(ext, filename)
        if ext == '.txt':
            file_path = os.path.join(settings.TXT_FOLDER, filename)
            lines = self.get_text_lines(file_path, from_lineno, to_lineno)
            is_excel = False
            header = None
        elif ext == '.xlsx':
            is_excel = True
            filename = filename[:-4] + 'txt'
            file_path = os.path.join(settings.EXCEL_FOLDER, filename)
            if not os.path.exists(file_path):
                raise Exception('No txt versions for the excel files, please run the command m parse_xl again')
            header, lines = self.get_excel_text_lines(file_path, from_lineno, to_lineno)

        ctx['lines'] = lines
        ctx['filename'] = filename
        ctx['lineno'] = lineno
        ctx['sample_lineno'] = sample.data_file_line
        ctx['prev'] = sample.get_text_link(line=lineno - OFFSET * 2 - 1)
        ctx['next'] = sample.get_text_link(line=lineno + OFFSET * 2 + 1)
        ctx['is_excel'] = is_excel
        ctx['header'] = header

        return ctx

    def get_text_lines(self, file_path, from_lineno, to_lineno):
        lines = []
        cur_lineno = 1
        with open(file_path, encoding="windows-1255") as fh:
            for line in fh:
                if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                    lines.append({'lineno': cur_lineno,
                                  'line': line.strip().encode('utf-8', errors='ignore')})
                cur_lineno += 1
        return lines

    def get_excel_text_lines(self, file_path, from_lineno, to_lineno):
        from xlparser.utils import HEADER_TO_STRING
        lines = []
        cur_lineno = 4
        first_line = True
        with open(file_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if first_line:
                    header = json.loads(line)
                    first_line = False
                else:
                    if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                        converted_line = [HEADER_TO_STRING[header[idx]](v) for idx, v in enumerate(json.loads(line))]
                        lines.append({'lineno': cur_lineno,
                                      'line': converted_line})
                    cur_lineno += 1
        return header, lines
