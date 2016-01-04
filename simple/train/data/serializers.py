from rest_framework import serializers
from rest_framework import fields
from rest_framework.reverse import reverse

from data import models


class RelationUrlField(serializers.CharField):
    def __init__(self, name, mapping, **kwargs):
        kwargs['read_only'] = True
        if not kwargs.pop('no_source', False):
            kwargs['source'] = '*'
        self.name = name
        self.mapping = mapping
        return super().__init__(**kwargs)

    def to_representation(self, value):
        kwargs = {}
        for k, v in self.mapping.items():
            kwargs[k] = getattr(value, v)
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
    services = RelationUrlField(name='route-services-list', mapping={'route_id': 'id'})
    trips = RelationUrlField(name='route-trips-list', mapping={'route_id':'id'})

    class Meta:
        model = models.Route
        fields = (
            'id',
            'stops',
            'services',
            'trips',
            'stops',
        )


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sample
        fields = (
            'index',
            'is_skipped',
            'valid',
            'actual_arrival',
            'exp_arrival',
            'delay_arrival',
            'actual_departure',
            'exp_departure',
            'delay_departure'
        )


class TripSerializer(serializers.ModelSerializer):
    id = fields.CharField()
    service = RelationUrlField(name='route-services-detail', no_source=True,mapping={
        'route_id': 'route_id',
        'pk':'pk'
    })
    route = serializers.HyperlinkedRelatedField(view_name='route-detail', read_only=True)
    samples = SampleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Trip
        fields = (
            'id',
            'valid',
            'train_num',
            'start_date',
            'service',
            'route',
            'samples',
        )


class ServiceSerializer(serializers.ModelSerializer):
    id = fields.CharField()
    stop_times = serializers.ListField(source='get_stop_times')

    class Meta:
        model = models.Service
        fields = (
            'id',
            'stop_times'
        )


