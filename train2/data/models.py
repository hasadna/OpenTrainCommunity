import datetime

import tabulate
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
import common.fields
import pytz
import geocoder

from data.utils import haversine

IST = pytz.timezone("Asia/Jerusalem")


class Trip(models.Model):
    route = models.ForeignKey('Route', null=True, related_name='trips')
    train_num = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    valid = models.BooleanField(default=True, db_index=True)
    invalid_reason = models.TextField(blank=True, null=True)

    x_week_day_local = models.IntegerField(blank=True, null=True)  # sunday 0 to saturday 6
    x_hour_local = models.IntegerField(blank=True, null=True)

    x_cache_version = models.IntegerField(default=0)
    x_max_delay_arrival = models.FloatField(null=True, blank=True)
    x_max2_delay_arrival = models.FloatField(null=True, blank=True)
    x_avg_delay_arrival = models.FloatField(null=True, blank=True)
    x_last_delay_arrival = models.FloatField(null=True, blank=True)
    x_before_last_delay_arrival = models.FloatField(null=True, blank=True)

    def complete_trip(self):
        try:
            self.attach_to_route(save=False)
        except Exception:
            if not self.valid:
                pass
            else:
                raise
        try:
            self.compute_cache(save=False)
        except Exception:
            if not self.valid:
                pass
            else:
                raise
        self.save()

    def compute_cache(self, save=True):
        self.x_hour_local = self.samples.earliest('index').exp_departure.astimezone(IST).hour
        self.x_week_day_local = self.date.isoweekday() % 7 #isoweekday is 1..7
        if save:
            self.save()

    def attach_to_route(self, save=True):
        stop_ids = list(self.samples.order_by('index').values_list('stop__gtfs_stop_id',flat=True))
        if stop_ids:
            self.route, __ = Route.objects.get_or_create(stop_ids=stop_ids)
            if save:
                self.save()
        else:
            assert not self.valid,'valid without stops???'

    def set_invalid(self, reason):
        self.valid = False
        self.invalid_reason = reason
        self.save()
        self.samples.all().update(valid=False, invalid_reason="trip is invalid")
        return self

    def check_trip(self):
        if not self.valid:
            # make sure all mark as invalid
            self.samples.filter(valid=True).update(valid=False, invalid_reason="trip is invalid")
            return
        samples = list(self.samples.all().order_by('index'))
        if not samples:
            return self.set_invalid('no samples')
        for sample in samples:
            sample.check_sample()
        fixed = [s for s in samples if s.actual_arrival_fixed and s.actual_departure_fixed]
        if len(fixed) >= 2:
            return self.set_invalid("more than 1 fix")
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

    def print_table(self):
        headers = ['index',
                  'name',
                  'gtfs_stop_id',
                  'exp_arrival',
                  'exp_departure',
                  'actual_arrival',
                  'actual_departure']

        def to_table_row(s):
            result = []
            for header in headers:
                if header == "name":
                    v = s.stop.english
                else:
                    v = getattr(s,header)
                result.append(v)
            return result

        t = tabulate.tabulate(
                          [to_table_row(s) for s in self.samples.all().order_by("index")],
                          headers=headers
                          )
        print(t)
    def __str__(self):
        return '{} #{} {}'.format(_('trip'),
                                  self.train_num,
                                  self.date
                                  )

    class Meta:
        unique_together = (('train_num', 'date'),)


class Route(models.Model):
    stop_ids = common.fields.ArrayField()

    def get_stops(self):
        stops_by_gtfs_id = dict((s.gtfs_stop_id, s) for s in Stop.objects.filter(gtfs_stop_id__in=self.stop_ids))
        return [stops_by_gtfs_id[gtfs_id] for gtfs_id in self.stop_ids]

    def get_first_stop(self):
        return Stop.objects.get(gtfs_stop_id=self.stop_ids[0])

    def get_last_stop(self):
        return Stop.objects.get(gtfs_stop_id=self.stop_ids[-1])

    def earliest_trip(self):
        return self.trips.earliest('date')

    def latest_trip(self):
        return self.trips.latest('date')

    def is_superset_of(self, route):
        from . import utils
        if route == self:
            return False
        return utils.is_list_in_list(route.stop_ids, self.stop_ids)

    def contains_stops(self, gtfs_stop_ids):
        from . import utils
        return utils.is_list_in_list(gtfs_stop_ids, self.stop_ids)

    def __str__(self):
        return '{} => {}'.format(self.get_first_stop(), self.get_last_stop())


class Sample(models.Model):
    stop = models.ForeignKey('Stop', related_name='samples')
    trip = models.ForeignKey('Trip', related_name='samples')

    gtfs_stop_id = models.IntegerField()

    is_source = models.BooleanField(default=False)
    is_dest = models.BooleanField(default=False)

    actual_arrival = models.DateTimeField(null=True)
    exp_arrival = models.DateTimeField(null=True)
    actual_departure = models.DateTimeField(null=True)
    exp_departure = models.DateTimeField(null=True)

    delay_arrival = models.FloatField(null=True)
    delay_departure = models.FloatField(null=True)

    index = models.IntegerField()

    filename = models.CharField(max_length=500)
    sheet_idx = models.IntegerField(default=0)
    line_number = models.IntegerField()

    valid = models.BooleanField(default=True, db_index=True)
    invalid_reason = models.TextField(blank=True, null=True)

    actual_departure_fixed = models.BooleanField(default=False)
    actual_arrival_fixed = models.BooleanField(default=False)

    ignored_error = models.TextField(blank=True, null=True)

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
                if v is None and f in ['actual_departure','actual_arrival']:
                    if f == 'actual_departure':
                        self.actual_departure = self.exp_departure
                        self.actual_departure_fixed = True
                    else:
                        self.actual_arrival = self.exp_arrival
                        self.actual_arrival_fixed = True
                    self.save()
                else:
                    self.valid = False
                    self.invalid_reason = 'missing {}'.format(f)
                    self.save()
                return

    class Meta:
        unique_together = (
            ('trip', 'index'),
            ('trip', 'stop'),
            ('filename', 'sheet_idx', 'line_number')
        )

    def __str__(self):
        return '{}'.format(self.stop.english)


class Stop(models.Model):
    gtfs_stop_id = models.IntegerField(db_index=True, unique=True)
    english = models.CharField(max_length=50)
    heb_short_name = models.CharField(max_length=50, blank=True, null=True)
    hebrew_list = ArrayField(models.CharField(max_length=100), default=[])
    lat = models.FloatField()
    lon = models.FloatField()
    gtfs_code = models.CharField(max_length=30, null=True)

    @cached_property
    def google_latlng(self):
        name = '{} {}'.format('תחנת רכבת', self.main_name)
        g = geocoder.google(name)
        return g.latlng

    def distance_to_google_latlng(self):
        if self.google_latlng:
            return haversine(self.latlon, self.google_latlng)
        return 0.0

    @property
    def main_name(self):
        if self.heb_short_name:
            return self.heb_short_name
        if self.hebrew_list:
            return self.hebrew_list[0]
        return self.english

    @property
    def latlon(self):
        return [self.lat, self.lon]

    @property
    def stop_name(self):
        return self.english

    @property
    def stop_short_name(self):
        return self.main_name

    def __str__(self):
        return self.main_name

    def save(self, *args, **kwargs):
        if self.heb_short_name and self.heb_short_name not in self.hebrew_list:
            self.hebrew_list.insert(0, self.heb_short_name)
        super().save(*args, **kwargs)

