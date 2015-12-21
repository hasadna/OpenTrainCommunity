from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import models
from . import serializers


class RoutesViewSet(ReadOnlyModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class TripViewSet(ReadOnlyModelViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
    def get_queryset(self):
        route_id = int(self.kwargs['route_id'])
        route = get_object_or_404(models.Route, pk=route_id)
        return route.trips.all()

