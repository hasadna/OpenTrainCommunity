from rest_framework import serializers
from rest_framework import fields
from rest_framework.reverse import reverse

from data import models


class RelationUrlField(serializers.CharField):
    def __init__(self, name, **kwargs):
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        self.name = name
        return super().__init__(**kwargs)

    def to_representation(self, value):
        if isinstance(value, models.Route):
            kwargs={'route_id': value.id}
        elif isinstance(value, models.Service):
            kwargs = {'route_id': value.route_id,
                      'service_id': value.id}

        return reverse(self.name, kwargs=kwargs, request=self.context['request'])


class StopSerializer(serializers.Serializer):
    latlon = fields.ListField(child=serializers.FloatField())
    stop_id = fields.IntegerField()
    stop_short_name = fields.CharField()
    heb_stop_names = fields.ListField(child=serializers.CharField())
    gtfs_stop_id = fields.IntegerField()
    stop_name = fields.CharField()


class RouteSerializer(serializers.ModelSerializer):
    id = fields.IntegerField()
    stops = StopSerializer(many=True, source='get_stops')
    services = RelationUrlField(name='route-services-list')
    trips = RelationUrlField(name='route-trips-list')

    class Meta:
        model = models.Route
        fields = (
            'id',
            'stops',
            'services',
            'trips',
            'stops',
        )


class TripSerializer(serializers.ModelSerializer):
    id = fields.CharField()

    class Meta:
        model = models.Trip
        fields = (
            'id',
        )


class ServiceSerializer(serializers.ModelSerializer):
    id = fields.CharField()

    class Meta:
        model = models.Service
        fields = (
            'id',
        )

