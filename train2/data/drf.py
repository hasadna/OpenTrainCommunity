from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import models
from . import serializers


class UnderRouteMixin(object):
    def get_route(self):
        route_id = int(self.kwargs['route_id'])
        return get_object_or_404(models.Route, pk=route_id)


# class UnderServiceMixin(UnderRouteMixin):
#     def get_service(self):
#         route = self.get_route()
#         service_id = int(self.kwargs['service_id'])
#         return get_object_or_404(route.services.all(), pk=service_id)


class RoutesViewSet(ReadOnlyModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


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
