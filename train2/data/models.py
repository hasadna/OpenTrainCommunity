from django.db import models
from django.utils.translation import ugettext as _
import common.fields


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

    index = models.IntegerField()

    filename = models.CharField(max_length=500)
    line_number = models.IntegerField()


class Stop(models.Model):
    gtfs_stop_id = models.IntegerField(db_index=True, unique=True)
    english = models.CharField(max_length=50)
    hebrews = common.fields.ArrayField()
    lat = models.FloatField()
    lon = models.FloatField()

    @property
    def main_name(self):
        if self.hebrews:
            return self.hebrews[0]
        return self.english

    def __str__(self):
        return '{} {} {}'.format(_('stop'),
                                 self.main_name,
                                 self.gtfs_stop_id
                                 )

