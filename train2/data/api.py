import json

from django.db.models import Count, Min, Max
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ViewSet
from rest_framework import exceptions
from . import models
from . import serializers
from . import utils
from . import logic


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


class RoutesViewSet(ReadOnlyModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer

    def resp_routes(self, routes):
        result = [{
                      'id': r.id,
                      'stop_ids': r.stop_ids,
                      'count': r.trips_count,
                      'min_date': utils.date_to_millis_since_epoch(r.min_date),
                      'max_date': utils.date_to_millis_since_epoch(r.max_date)
                  } for r in routes]

        return Response(result)

    @list_route()
    def all(self, request):
        min_count = int(self.request.GET.get('min_count',10))
        routes = list(models.Route.objects.all().order_by('id').annotate(
            trips_count=Count('trips'),
            min_date=Min('trips__date'),
            max_date=Max('trips__date')))

        routes = [r for r in routes if r.trips_count > min_count]
        return self.resp_routes(routes)

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
        return self.resp_routes(routes)


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
        from_date = utils.parse_date(request.GET['from_date'])
        to_date = utils.parse_date(request.GET['to_date'])
        result = logic.get_from_to_info_full(origin_id=from_id,
                                             destination_id=to_id,
                                             from_date=from_date,
                                             to_date=to_date)
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


class RoutesViewSet(ReadOnlyModelViewSet):
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
        data = []
        with open("../simple/train/data/analysis/routes_output_format_records.json") as fh:
            for line in fh:
                data.append(json.loads(line))
        return Response(data=data)




