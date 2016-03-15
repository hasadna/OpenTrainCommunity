import datetime
from django.db import models
from django.utils.translation import ugettext as _
import common.fields


class Trip(models.Model):
    route = models.ForeignKey('Route', null=True, related_name='trips')
    train_num = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    valid = models.BooleanField(default=True, db_index=True)
    invalid_reason = models.TextField(blank=True, null=True)

    def set_invalid(self, reason):
        self.valid = False
        self.invalid_reason = reason
        self.save()
        return self

    def check_trip(self):
        samples = list(self.samples.all().order_by('index'))
        if not samples:
            return self.set_invalid('no stops')
        for sample in samples:
            sample.check_sample()
        invalid = [s for s in samples if not s.valid]
        if invalid:
            return self.set_invalid(invalid[0].invalid_reason)
        is_dest = [s for s in samples if s.is_dest]
        if not is_dest:
            return self.set_invalid('no is_dest')
        if len(is_dest) > 1:
            return self.set_invalid('more than 1 is_dest')
        is_source = [s for s in samples if s.is_source]
        if not is_source:
            return self.set_invalid('no is_source')
        if len(is_source) > 1:
            return self.set_invalid('more than 1 is_source')
        if not samples[0].is_source:
            self.set_invalid('first stop is not is_source')
        if not samples[-1].is_dest:
            self.set_invalid('last stop is not is_dest')

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

    valid = models.BooleanField(default=True, db_index=True)
    invalid_reason = models.TextField(blank=True, null=True)

    def check_sample(self):
        if self.is_source:
            required_fields = ['actual_departure','exp_departure']
        elif self.is_dest:
            required_fields = ['actual_arrival','exp_arrival']
        else:
            required_fields = ['actual_arrival','exp_arrival', 'actual_departure', 'exp_departure']
        for f in required_fields:
            v = getattr(self, f)
            if v is None or not isinstance(v, datetime.datetime):
                self.valid = False
                self.invalid_reason = 'missing {}'.format(f)
                self.save()
                return



    class Meta:
        unique_together = (
            ('trip', 'index'),
            ('trip', 'stop'),
            ('filename', 'line_number')
        )

    def __str__(self):
        return '{}'.format(self.stop.english)



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
