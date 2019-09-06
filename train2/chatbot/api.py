import time
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import serializers, models

logger = logging.getLogger(__name__)


class CancelReportsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = serializers.ChatReportSerializer
    queryset = models.ChatReport.objects.filter(real_report=True)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        if settings.DEBUG:
            cache_key = 'cacnel-reprots-api'
            data = cache.get(cache_key)
            if data:
                return Response(data=data)
            t1 = time.time()
            resp = super().list(request, *args, **kwargs)
            t2 = time.time()
            logger.info("Took %.2f", t2-t1)
            cache.set(cache_key, resp.data, 3600)
            return resp
        return super().list(request, *args, **kwargs)


class TripViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = serializers.TripSerializer
    queryset = models.ChatReportTrip.objects.all()
    pagination_class = None


