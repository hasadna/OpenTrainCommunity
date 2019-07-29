from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from . import serializers, models


class CancelReportsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = serializers.ChatReportSerializer
    queryset = models.ChatReport.objects.filter(real_report=True)
    pagination_class = None


class TripViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = serializers.TripSerializer
    queryset = models.ChatReportTrip.objects.all()
    pagination_class = None


