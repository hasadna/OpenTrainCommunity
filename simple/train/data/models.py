from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
import pytz
from django.utils.translation import ugettext as _
from data import cache_utils

ISRAEL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class Sample(models.Model):
    """
    README:
    =======
    this model represents one line in the input
    Note that lines were dumped to DB after groups to trips and after several checks
    Each line belong to trip, and in each day the combination of train_num,start_date should be unique
    The trip_id is string combination of train num and start date
    If there was eny error in the trip then all its samples are marked as valid = False, you can filter it out
    The exp arrival and exp departure should be None only in first/last stop respectively.
    The actual arrival and actual departure should be None in first/last stop respectively, but can be also None if the sample is missing
    If there is no actual arrival or actual departure, then the delay is None also.

    Note that there are samples for real stops and for midpoints in the way, as given by the train. 
    and their name is prefixed with -

    """
    index = models.IntegerField()  # the index of the stop in the trip (0 based)
    stop_id = models.IntegerField(db_index=True)  # the stop id
    stop_name = models.CharField(
        max_length=100)  # the stop name in english - not formal name, if this is not real stop will be prefixed with -
    #is_real_stop = models.BooleanField(default=False)  # true is this is real stop
    is_skipped = models.BooleanField(default=False) # true if this is skipped stop
    valid = models.BooleanField(default=False,
                                db_index=True)  # true if this is stop in valid trip (e.g. with no errros)
    is_first = models.BooleanField(default=False)  # true if this is the first stop of the trip (index = 0)
    is_last = models.BooleanField(default=False)  # true if this is the last stop
    actual_arrival = models.DateTimeField(blank=True,
                                          null=True)  # actual arrival time with tz, will be None if there is no such
    exp_arrival = models.DateTimeField(blank=True,
                                       null=True)  # exp arrival time with tz, will be None if this is the first stop
    delay_arrival = models.FloatField(blank=True, null=True)  # the delay in the arrival in seconds
    actual_departure = models.DateTimeField(blank=True,
                                            null=True)  # actual depart time with tz, will be None if there is no such
    exp_departure = models.DateTimeField(blank=True,
                                         null=True)  # exp depart time with tz, will be None if this is the last stop
    delay_departure = models.FloatField(blank=True, null=True)  # the delay in the departure in seconds
    data_file = models.CharField(max_length=100)  # the name of the data file (text file)
    data_file_line = models.IntegerField()  # the line number in the data file (text file)
    trip = models.ForeignKey('Trip', blank=True, null=True)

    def get_parent(self):
        return self.trip

    def get_short_name(self):
        return _('Sample') + unicode(self.id)

    def get_text_link(self,line=None):
        if line is None:
            line = self.data_file_line
            anchor = '#%s' % line
        else:
            anchor = ''
        return '/browse/raw-data/?file=%s&line=%s&sample_id=%s%s' % (self.data_file,
                                                                      line,
                                                                      self.id,
                                                                      anchor)

    def print_nice(self):
        print '%2d) %-20s %s' % (self.index,
                                 self.stop_name,
                                 self.actual_arrival)

    def to_local_str_hm(self, dt, sep=''):
        if not dt:
            return '----'
        ldt = dt.astimezone(ISRAEL_TIMEZONE)
        return ldt.strftime('%H' + sep + '%M')

    def get_exp_time_string(self):
        """
        :return: HHMMHHMM of exp arrival and exp departure (or ----)
        """
        return '%s%s' % (self.to_local_str_hm(self.exp_arrival),
                         self.to_local_str_hm(self.exp_departure))

    def to_json(self):
        import services

        stop_name = services.get_stop_name(self.stop_id, self.stop_name)

        def remove_site(link):
            import re

            result = re.sub('http://.*?/', '/', link)
            return result

        return {'index': self.index,
                'stop_id': self.stop_id,
                'stop_name': stop_name,
                'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
                'exp_arrival': self.exp_arrival.isoformat() if self.exp_arrival else None,
                'delay_arrival': self.delay_arrival,
                'actual_departure': self.actual_departure.isoformat() if self.actual_departure else None,
                'exp_departure': self.exp_departure.isoformat() if self.exp_departure else None,
                'delay_departure': self.delay_departure,
                'link': remove_site(self.data_file_link)
        }


class Service(models.Model):
    route = models.ForeignKey('Route')
    trips = models.ManyToManyField('Trip')
    local_time_str = models.TextField(default=None)

    def get_parent(self):
        return self.route

    def get_short_name(self):
        return '%s %s: %s %s %s' % (_('Service'),
                                    self.id,
                                    self.get_departure_time_str(),
                                    _('to'),
                                    self.get_arrival_time_str())

    def get_departure_time_str(self):
        trip = self.trips.all()[0]
        first_sample = trip.sample_set.filter(valid=True).earliest('index')
        return first_sample.to_local_str_hm(first_sample.exp_departure, ':')

    def get_arrival_time_str(self):
        trip = self.trips.all()[0]
        last_sample = trip.sample_set.filter(valid=True).latest('index')
        return last_sample.to_local_str_hm(last_sample.exp_arrival, ':')

    def get_total_time_str(self):
        trip = self.trips.all()[0]
        first_sample = trip.sample_set.filter(valid=True).earliest('index')
        last_sample = trip.sample_set.filter(valid=True).latest('index')
        total_secs = (last_sample.exp_arrival - first_sample.exp_departure).total_seconds()
        total_minutes = total_secs / 60
        hours,minutes = divmod(total_minutes,60)

        return '%d:%02d' % (hours,minutes)

    def get_skipped_stop_ids(self):
        stats = self.get_stats_dict()
        stop_ids = self.route.stop_ids
        result = []
        for stop_id in stop_ids:
            stop_stat = stats[stop_id]
            if stop_stat['time_in_stop'] is not None and stop_stat['time_in_stop'] < 5:
                result.append(stop_id)
        return result


    @cache_utils.cache_obj_method
    def get_stats_list(self):
        import data.api
        return data.api.get_service_stat(self)

    def get_stats_dict(self):
        stats = self.get_stats_list()
        stats_by_stop_id = dict()
        for stat in stats:
            stats_by_stop_id[stat['stop_id']] = stat
        return stats_by_stop_id

    def get_stops(self):
        import services
        stats = self.get_stats_dict()
        trip = self.trips.first()
        samples = trip.get_real_stop_samples()
        result = []
        for sample in samples:
            stop_stat = stats[sample.stop_id]
            result.append({
                'stop_id': sample.stop_id,
                'stop_name': services.get_heb_stop_name(sample.stop_id),
                'exp_arrival': sample.to_local_str_hm(sample.exp_arrival, ':'),
                'exp_departure': sample.to_local_str_hm(sample.exp_departure, ':'),
                'stat': stop_stat,
                'can_be_skipped': stop_stat['time_in_stop'] is not None and stop_stat['time_in_stop'] < 5
            })
        return result


class Trip(models.Model):
    id = models.CharField(primary_key=True, max_length=30, db_index=True, unique=True)
    train_num = models.IntegerField(db_index=True)
    start_date = models.DateField(db_index=True)
    valid = models.BooleanField(default=False)
    route = models.ForeignKey('Route')
    trip_name = models.CharField(max_length=30,
                                 db_index=True)  # generated id for the given trip (combination of train num and date)
    train_num = models.IntegerField(db_index=True)  # the train num as given in the text files
    start_date = models.DateField(
        db_index=True)  # the start date of the trip (note that trip can be spanned over two days)


    def get_parent(self):
        return self.service_set.all()[0]

    def get_short_name(self):
        return '%s %s %s %s' % (
            _('Trip'),
            self.id,
            _('on'),
            self.start_date.strftime('%d/%m/%Y'))

    def get_exp_time_strings(self):
        """
        :return: common separated string of all exp time in local time
        """
        samples = list(self.get_real_stop_samples())
        samples = [samples[0],samples[-1]]
        return ','.join(s.get_exp_time_string() for s in samples)

    def get_real_stop_samples(self):
        stop_ids = self.route.stop_ids
        return self.sample_set.filter(valid=True, stop_id__in=stop_ids).order_by('index')

    def to_json(self):
        stops = self.get_real_stop_samples()
        return {'id': self.id,
                'train_num': self.train_num,
                'start_date': self.start_date.isoformat(),
                'valid': self.valid,
                'stops': stops,
                'is_to_north': self.route.is_to_north()
        }

    def print_nice(self):
        samples = self.sample_set.filter(is_real_stop=True).order_by('index')
        for sample in samples:
            sample.print_nice()


class Route(models.Model):
    stop_ids = ArrayField(base_field=models.IntegerField(),db_index=True, unique=True)

    def skip_stop_ids(self, stop_ids):
        for stop_id in stop_ids:
            if stop_id not in self.stop_ids:
                raise Exception('Stop %s is not part of the stop ids' % stop_id)
        for stop_id in stop_ids:
            self.stop_ids.remove(stop_id)
            self.save()

    def unskip_stop_ids(self,stop_ids):
        assert False,'not yet'


    def is_to_north(self):
        import services

        first_stop = services.get_stop(self.stop_ids[0])
        last_stop = services.get_stop(self.stop_ids[-1])
        return first_stop['latlon'][0] < last_stop['latlon'][0]

    def get_parent(self):
        return None

    def get_short_name(self):
        import services

        return '%s %s: %s %s %s' % (_('Route'),
                                    self.id,
                                    services.get_heb_stop_name(self.stop_ids[0]),
                                    '&#8604;',
                                    services.get_heb_stop_name(self.stop_ids[-1]))

    def print_nice(self):
        import services

        for idx, stop_id in enumerate(self.stop_ids):
            print '%2d %s' % (idx, services.get_stop_name(stop_id))


    def get_services(self):
        return self.service_set.all().order_by('id')

    def group_into_services(self):
        from itertools import groupby

        trips = self.trip_set.filter(valid=True)
        group_it = groupby(trips, key=lambda t: t.get_exp_time_strings())
        for k, trips_it in group_it:
            s = Service.objects.get_or_create(route=self,
                                              local_time_str=k
            )[0]
            s.trips.add(*list(trips_it))


    def get_stops(self):
        import services

        return services.get_stops(self.stop_ids)

    def first_stop_id(self):
        return self.stop_ids[0]

    def last_stop_id(self):
        return self.stop_ids[-1]

    def admin_unicode(self):
        import services

        first_stop_name = services.get_heb_stop_name(self.stop_ids[0])
        last_stop_name = services.get_heb_stop_name(self.stop_ids[-1])

        result = '%s: %s stops from %s to %s' % (self.id,
                                                 len(self.stop_ids),
                                                 first_stop_name,
                                                 last_stop_name,
        )
        return unicode(result)

