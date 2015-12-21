from rest_framework import serializers
from rest_framework import fields
from data import models


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

    class Meta:
        model = models.Route
        fields = (
            'id',
            'stops'
        )


class TripSerializer(serializers.ModelSerializer):
    id = fields.CharField()

    class Meta:
        model = models.Trip
        fields = (
            'id',
        )


