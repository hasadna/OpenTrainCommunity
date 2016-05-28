import urllib
import json
import os.path

from django.conf import settings

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
        return urllib.parse.urljoin(settings.BASE_URL, reverse(self.name, kwargs=kwargs, request=None))


class RouteUrlAndIdField(serializers.ReadOnlyField):
    def to_representation(self, value):
        return {
            'id': value.id,
            'url': urllib.parse.urljoin(settings.BASE_URL, reverse('route-detail', kwargs={'pk':value.id},request=None))
        }


class StopSerializer(serializers.ModelSerializer):
    stop_id = serializers.IntegerField(source='gtfs_stop_id')
    heb_stop_names = serializers.ReadOnlyField(source='hebrews')
    latlon = serializers.ReadOnlyField()
    google_url = serializers.SerializerMethodField()

    def get_google_url(self, obj):
        return 'https://www.google.co.il/maps/@{lat},{lon},17z?hl=iw'.format(lat=obj.lat,
                                                                             lon=obj.lon)

    class Meta:
        model = models.Stop
        fields = (
            'id',
            'stop_id',
            'heb_stop_names',
            'latlon',
            'stop_name',
            'stop_short_name',
            'google_url',
        )


class RouteSerializer(serializers.ModelSerializer):
    id = fields.IntegerField()
    stops = StopSerializer(many=True, source='get_stops')
    #services = RelationUrlField(name='route-services-list', mapping={'route_id': 'id'})
    trips = RelationUrlField(name='route-trips-list', mapping={'route_id':'id'})
    trips_count = serializers.SerializerMethodField()

    def get_trips_count(self, obj):
        return obj.trips.count()

    class Meta:
        model = models.Route
        fields = (
            'id',
            'stops',
           # 'services',
            'trips',
            'trips_count',
            'stops',
        )


class SampleSerializer(serializers.ModelSerializer):
    stop = StopSerializer(source='get_stop')

    class Meta:
        model = models.Sample
        fields = (
            'index',
            'valid',
            'actual_arrival',
            'exp_arrival',
            'delay_arrival',
            'actual_departure',
            'exp_departure',
            'delay_departure',
            'stop',
        )


class TripSerializer(serializers.ModelSerializer):
    id = fields.CharField()
    service = RelationUrlField(name='route-services-detail', no_source=True,mapping={
        'route_id': 'route_id',
        'pk':'pk'
    })
    route = RouteUrlAndIdField()
    samples = SampleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Trip
        fields = (
            'id',
            'valid',
            'train_num',
            'date',
            'service',
            'route',
            'samples',
        )

#
# class ServiceSerializer(serializers.ModelSerializer):
#     id = fields.CharField()
#     stop_times = serializers.ListField(source='get_stop_times')
#
#     class Meta:
#         model = models.Service
#         fields = (
#             'id',
#             'stop_times'
#         )
#


def json_trips_line_by_line(trips, ofile):
    """
    :param trips: qs or list of trips
    :param ofile: output file (will be deleted)
    :return: None
    """
    with open(ofile, 'w') as fh:
        count = 0
        for idx, t in enumerate(trips):
            json.dump(TripSerializer(t).data, fh)
            fh.write('\n')
            if (idx + 1) % 500 == 0:
                print('{} completed'.format(1+idx))
            count += 1
        print('{0} trips were written into {1}'.format(count, ofile))


def all_routes_trips_line_by_line(routes, base_dir):
    for idx, r in enumerate(routes):
        trips = r.trips.all()
        print('{}: Starting route {} with {} trips'.format(idx, r.id, trips.count()))
        json_trips_line_by_line(trips,os.path.join(base_dir, 'route_{0}.json'.format(r.id)))

