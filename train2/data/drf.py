from django.db.models import Count, Min, Max
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import models
from . import serializers
from . import utils

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


class RoutesViewSet(ReadOnlyModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer

    @list_route()
    def all(self, request):
        min_count = self.request.GET.get('min_count',10)
        routes = list(models.Route.objects.all().order_by('id').annotate(
            trips_count=Count('trips'),
            min_date=Min('trips__date'),
            max_date=Max('trips__date')))

        routes = [r for r in routes if r.trips_count > min_count]
        result = []
        for r in routes:
            result.append({
                'id': r.id,
                'stop_ids': r.stop_ids,
                'count': r.trips_count,
                'min_date': utils.encode_date(r.min_date),
                'max_date': utils.encode_date(r.max_date)
            })

        return Response(result)


class RouteTripsViewSet(UnderRouteMixin, ReadOnlyModelViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer

    def get_queryset(self):
        return self.get_route().trips.all()


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
