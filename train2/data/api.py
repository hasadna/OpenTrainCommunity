import calendar
import os
import json
import datetime
import logging
import time


from django.core.cache import cache
from django.db.models import Count, Min, Max, IntegerField, Value, Case, When, \
    Sum
from django.conf import settings
from django.db.models.functions import ExtractYear, ExtractMonth
from django.templatetags.static import static
from django.utils import timezone
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ViewSet
from rest_framework import exceptions, mixins
from . import models
from . import serializers
from . import utils
from . import logic


logger = logging.getLogger(__name__)


class UnderRouteMixin(object):
    def get_route(self):
        route_id = int(self.kwargs['route_id'])
        return get_object_or_404(models.Route, pk=route_id)


# class UnderServiceMixin(UnderRouteMixin):
#     def get_service(self):
#         route = self.get_route()
#         service_id = int(self.kwargs['service_id'])
#         return get_object_or_404(route.services.all(), pk=service_id)


class StopViewSet(ReadOnlyModelViewSet):
    queryset = models.Stop.objects.all()
    serializer_class = serializers.StopSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @list_route(methods=['GET'], url_path='from-to')
    def from_to(self, request):
        """
        list of stop ids from from_stop to to_stop
        """
        try:
            from_id = int(request.GET['from_stop'])
            to_id = int(request.GET['to_stop'])
        except KeyError:
            raise exceptions.APIException("from_stop and to_stop are mandatory")

        try:
            models.Stop.objects.get(gtfs_stop_id=from_id)
        except models.Stop.DoesNotExist:
            raise exceptions.APIException("illegal from_stop {}".format(from_id))

        try:
            models.Stop.objects.get(gtfs_stop_id=to_id)
        except models.Stop.DoesNotExist:
            raise exceptions.APIException("illegal to_stop {}".format(to_id))

        return Response(data=logic.get_stops_from_to(from_id, to_id))

class StatViewSet(GenericViewSet):
    def get_queryset(self):
        return None

    @list_route(url_path="path-info-full")
    def path_info_full(self, request):
        origin = int(request.GET['origin'])
        destination = int(request.GET['destination'])
        from_date = utils.parse_date(request.GET.get('from_date'))
        to_date = utils.parse_date(request.GET.get('to_date'))
        if from_date and to_date and from_date > to_date:
            raise exceptions.APIException('from_date {} cannot be after to_date {}'.format(from_date, to_date))
        result = logic.get_path_info_full(origin, destination, from_date, to_date)
        return Response(result)

    @list_route(url_path='route-info-full')
    def route_info(self, request):
        route_id = request.GET['route_id']
        from_date = utils.parse_date(request.GET.get('from_date'))
        to_date = utils.parse_date(request.GET.get('to_date'))
        if from_date and to_date and from_date > to_date:
            raise ValueError('from_date %s cannot be after to_date %s' % (from_date, to_date))
        result = logic.get_route_info_full(route_id, from_date, to_date)
        return Response(result)

    @list_route(url_path='from-to-full')
    def from_to_full(self, request):
        from_id = int(request.GET['from_stop'])
        to_id = int(request.GET['to_stop'])
        skipped_ids = list(map(int, request.GET.get('skipped').split(","))) if request.GET.get('skipped') else None
        skipped_complement = request.GET.get('skipped_complement', '0') == '1'
        from_date = utils.parse_date(request.GET['from_date'])
        to_date = utils.parse_date(request.GET['to_date'])
        result = logic.get_from_to_info_full(origin_id=from_id,
                                             destination_id=to_id,
                                             from_date=from_date,
                                             to_date=to_date,
                                             skipped_ids=skipped_ids,
                                             skipped_complement=skipped_complement)
        return Response(result)


class GeneralViewSet(ViewSet):
    @list_route(url_path='dates-range')
    def dates_range(self, request, *args, **kwargs):
        first_trip_date = models.Trip.objects.order_by('date').first()
        last_trip_date = models.Trip.objects.order_by('date').last()
        data = {
            'first_date': {
                'month': first_trip_date.date.month,
                'year': first_trip_date.date.year,
            },
            'last_date': {
                'month': last_trip_date.date.month,
                'year': last_trip_date.date.year,
            }
        }
        return Response(data=data)

    @list_route(url_path='sleep')
    def goto_sleep(self, request, *args, **kwargs):
        from django.db import connection
        """ for some testings """
        sleep_id = int(request.GET.get('id'))
        sleep_time = int(request.GET.get('time'))
        start_time = timezone.now()
        logger.info("[%d] Going to sleep %d", sleep_id, sleep_time)
        with connection.cursor() as c:
            c.execute("select pg_sleep({})".format(sleep_time))
            print(c.fetchall())

        logger.info("[%d] After sleep %d", sleep_id, sleep_time)
        return Response({
            'sleep_id': sleep_id,
            'start_time': start_time,
            'end_time': timezone.now(),
            'sleep_time': sleep_time
        })


class RoutesViewSet(ReadOnlyModelViewSet):
    # TODO: This class is redeclared and shadows earlier def. Should one of them be removed ?
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer

    @list_route()
    def all(self, request):
        min_count = int(self.request.GET.get('min_count',10))
        routes = list(models.Route.objects.all().order_by('id').annotate(
            trips_count=Count('trips'),
            min_date=Min('trips__date'),
            max_date=Max('trips__date')))

        routes = [r for r in routes if r.trips_count > min_count]
        result = [{
            'id': r.id,
            'stop_ids': r.stop_ids,
            'count': r.trips_count,
            'min_date': utils.date_to_millis_since_epoch(r.min_date),
            'max_date': utils.date_to_millis_since_epoch(r.max_date)
        } for r in routes]

        return Response(result)

    @list_route(url_path='all-by-date')
    def all_by_date(self, request):
        min_count = int(self.request.GET.get('min_count',10))
        from_date = utils.parse_date(request.GET['from_date'])
        to_date = utils.parse_date(request.GET['to_date'])

        routes = list(models.Route.objects
                    .filter(trips__date__gte=from_date, trips__date__lte=to_date)
                    .annotate(trips_count=Count('trips'))
                    .filter(trips_count__gt=min_count)
                    .order_by('id'))

        result = [{
                      'id': r.id,
                      'stop_ids': r.stop_ids,
                      'count': r.trips_count
                  } for r in routes]
        return Response(result)


class RouteTripsViewSet(UnderRouteMixin, ReadOnlyModelViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer

    def get_queryset(self):
        return self.get_route().trips.all()


class TripViewSet(mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer

    @list_route(methods=['GET'],
                url_path='compact',
                serializer_class=serializers.TripCompactSerializer)
    def list_compact(self, request):
        start_date = utils.parse_date(request.GET['start_date'], reverse=True)
        end_date = utils.parse_date(request.GET['end_date'], reverse=True)
        key = 'trips:compact:{}:{}'.format(start_date, end_date)
        data = cache.get(key)
        if not data:
            logger.info(">>> for %s => %s from cache", start_date, end_date)
            queryset = models.Trip.objects.filter(valid=True).filter(date__gte=start_date, date__lte=end_date)
            queryset = queryset.annotate(samples_count=Count('samples'))
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(key, data)
        return Response(data)


class HeatMapViewSet(ViewSet):
    def list(self, request):
        import data.analysis.heatmap_utils
        heatmap_dict = data.analysis.heatmap_utils.run()
        heatmap = [
            {
                'stop_id': k,
                'score': v,
            } for k,v in heatmap_dict.items()
        ]
        return Response(data=heatmap)

# class ServiceTripsViewSet(UnderServiceMixin, ReadOnlyModelViewSet):
#     queryset = models.Trip.objects.all()
#     serializer_class = serializers.TripSerializer
#
#     def get_queryset(self):
#         return self.get_service().trips.all()
#
#
# class RouteServicesViewSet(UnderRouteMixin, ReadOnlyModelViewSet):
#     queryset = models.Service.objects.all()
#     serializer_class = serializers.ServiceSerializer
#
#     def get_queryset(self):
#         return self.get_route().services.all()
#
#

class HighlightsViewSet(ViewSet):
    def list(self, request, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, "analysis/static/analysis/routes_output_format_records.json")
        with open(path) as fh:
            data = [json.loads(line) for line in fh]
        return Response(data={
            'highlights': data,
            'url': static('analysis/routes_output.xlsx')
        })

    # @list_route()
    def top(self, request, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, "analysis/static/analysis/manual_highlights.json")
        with open(path) as fh:
            data = json.load(fh)
        return Response(data={
            'highlights': data,
        })


class RealRoutesViewSet(ViewSet):
    def list(self, request, *args, **kwargs):
        m = int(kwargs['month'])
        y = int(kwargs['year'])
        from_date = datetime.date(y, m ,1)
        wd, num_days = calendar.monthrange(y, m)
        to_date = datetime.date(y, m, num_days)
        routes = logic.find_real_routes(from_date, to_date)
        serializer = serializers.RealRouteSerializer(routes, many=True)
        return Response(status=200,
                        data=serializer.data)


class MonthlyViewSet(GenericViewSet):
    def list(self, request):
        start_month = int(request.query_params['start_month'])
        start_year = int(request.query_params['start_year'])
        end_month = int(request.query_params['end_month'])
        end_year = int(request.query_params['end_year'])

        start_date = datetime.date(start_year, start_month, 1)
        _, num_days = calendar.monthrange(end_year, end_month)
        end_date = datetime.date(end_year,end_month, num_days)

        trips_qs = models.Trip.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            valid=True)
        delays_by_month = list(
            trips_qs.annotate(
                y=ExtractYear('date'), m=ExtractMonth('date')
            ).values(
                'y', 'm'
            ).annotate(
                count=Count('id')
            ).annotate(
                count_late_max=Sum(Case(When(x_max_delay_arrival__gte=300, then=Value(1)),
                    default=Value(0), output_field=IntegerField()))
            ).annotate(
                count_late_last=Sum(Case(When(x_last_delay_arrival__gte=300, then=Value(1)),
                    default=Value(0), output_field=IntegerField()))
            )
        )
        delays_by_month.sort(key=lambda x: (x['y'], x['m']))
        return Response(data=delays_by_month)

    @list_route(url_path='year-months')
    def get_last_year_month(self, request):
        last_trip = models.Trip.objects.order_by('-date').first()
        last_month = last_trip.date.month
        last_year = last_trip.date.year
        return Response(data={
            'last': [last_year, last_month],
            'first': [2017, 1]
        })



