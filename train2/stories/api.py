import hashlib
import json

from rest_framework import exceptions
from rest_framework.decorators import list_route
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import GenericViewSet

from . import models


class StoriesThrottle(AnonRateThrottle):
    rate = '10/minute'


class StoriesViewSet(
    RetrieveModelMixin,
    GenericViewSet):

    queryset = models.Story.objects.all()

    @list_route(url_path='share', methods=['post'], throttle_classes=[StoriesThrottle])
    def share(self, request, *args, **kwargs):
        dump = request.data['dump']
        dumped_json = json.dumps(dump, sort_keys=True)
        if len(dumped_json) > 10000:
            raise exceptions.ValidationError('too big')

        checksum = hashlib.md5(dumped_json.encode('utf-8')).hexdigest()
        instance = models.Story.objects.filter(checksum=checksum).first()
        if not instance:
            instance = models.Story.objects.create(
                dump=dump,
                checksum=checksum
            )
        return self.resp(instance, status=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.resp(instance, status=200)

    def resp(self, instance, status):
        return Response(data={
            'dump': instance.dump,
            'id': instance.id,
        }, status=status)


