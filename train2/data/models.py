from django.db import models
from django.utils.translation import ugettext as _
import common.fields


class Trip(models.Model):
    route = models.ForeignKey('Route', null=True, related_name='trips')
    train_num = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return '{} #{} {}'.format(_('trip'),
                                  self.train_num,
                                  self.date
                                  )

    class Meta:
        unique_together = (('train_num', 'date'),)


class Route(models.Model):
    stop_ids = common.fields.ArrayField()


class Sample(models.Model):
    stop = models.ForeignKey('Stop', related_name='samples')
    trip = models.ForeignKey('Trip', related_name='samples')

    is_source = models.BooleanField(default=False)
    is_dest = models.BooleanField(default=False)

    actual_arrival = models.DateTimeField(null=True)
    exp_arrival = models.DateTimeField(null=True)
    actual_departure = models.DateTimeField(null=True)
    exp_departure = models.DateTimeField(null=True)

    index = models.IntegerField()

    filename = models.CharField(max_length=500)
    line_number = models.IntegerField()

    class Meta:
        unique_together = (
            ('trip', 'index'),
            ('trip', 'stop'),
            ('filename', 'line_number')
        )


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
