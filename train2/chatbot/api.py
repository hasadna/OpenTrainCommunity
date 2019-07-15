from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from . import serializers, models


class CancelReportsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = serializers.ChatReportSerializer
    queryset = models.ChatReport.objects.all()
    pagination_class = None
