from django.db import models
import common.fields


class StopKind:
    MIDDLE = 'MIDDLE'
    DEST = 'DEST'
    DEST_COMER = 'DEST_COMER'
    DEST_OPER = 'DEST_OPER'
    ORIG = 'ORIG'
    ORIG_COMER = 'ORIG_COMER'
    ORIG_OPER = 'ORIG_OPER'
    choices = ((MIDDLE, 'middle'),
               (DEST, 'destination'),
               (DEST_COMER, 'destination commercial'),
               (DEST_OPER, 'destination operational'),
               (ORIG, 'origin'),
               (ORIG_COMER, 'origin commercial'),
               (ORIG_OPER, 'origin operational'))


class Trip(models.Model):
    route = models.ForeignKey('Route', null=True)
    train_num = models.IntegerField(db_index=True)
    train_date = models.DateField(db_index=True)
    is_planned_trip = models.BooleanField()


class Route(models.Model):
    stop_ids = common.fields.ArrayField()


class Sample(models.Model):
    stop = models.ForeignKey('Stop')
    trip = models.ForeignKey('Trip')

    actual_arrival = models.DateTimeField(null=True)
    exp_arrival = models.DateTimeField(null=True)
    actual_departure = models.DateTimeField(null=True)
    exp_departure = models.DateTimeField(null=True)

    is_stopped = models.BooleanField()
    is_planned = models.BooleanField()
    index = models.IntegerField()
    stop_kind = models.CharField(max_length=30, choices=StopKind.choices)


class Stop(models.Model):
    stop_id = models.IntegerField()
    stop_name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()

