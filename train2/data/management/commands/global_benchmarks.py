from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import logging
import datetime
import data.stop_utils
from django.utils.translation import activate
from data.models import Sample
from data.models import Stop
from data.models import Trip
from django.db.models import Avg
from django.db.models import Max

# Run this file using: python manage.py global_benchmarks


LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for day in range(7):
            self.compute_samples_per_day(day+1)

        for hour in range(24):
            self.compute_samples_per_hour(hour)

        for day in range(7):
            self.compute_trips_per_day(day+1)

        for hour in range(24):
            self.compute_trips_per_hour(hour)

    def compute_trips_per_day(self, day):
        ok_qs = Trip.objects.filter(valid=True,date__gte=datetime.date(2017,5,1), date__week_day=day).annotate(c=Max('samples__delay_arrival'))
        late_qs = ok_qs.filter(c__gte=300)
        print('Trips with some late station for day = {} % = {}'.format(day, 100.0*late_qs.count()/ok_qs.count()))

    def compute_trips_per_hour(self, hour):
        ok_qs = Trip.objects.filter(valid=True,date__gte=datetime.date(2017,5,1), x_hour_local=hour).annotate(c=Max('samples__delay_arrival'))
        late_qs = ok_qs.filter(c__gte=300)
        print('Trips with some late station for hour = {} % = {}'.format(hour, 100.0*late_qs.count()/ok_qs.count()))

    def compute_samples_per_day(self, day):
        samples_ontime = Sample.objects.filter(delay_arrival__lt=5*60).filter(exp_arrival__week_day=day+1).filter(valid=True,exp_arrival__gte=datetime.date(2017,5,1)).count()
        samples_delayed = Sample.objects.filter(delay_arrival__gte=5*60).filter(exp_arrival__week_day=day+1).filter(valid=True,exp_arrival__gte=datetime.date(2017,5,1)).count()
        ontime_average = samples_ontime / (samples_ontime + samples_delayed)
        print("Samples for day %d Ontime (less than 5 minutes delay): %.2f " % (day, ontime_average))

    def compute_samples_per_hour(self, hour):
        samples_ontime = Sample.objects.filter(delay_arrival__lt=5*60).filter(exp_arrival__week_day=hour).filter(valid=True,exp_arrival__gte=datetime.date(2017,5,1)).count()
        samples_delayed = Sample.objects.filter(delay_arrival__gte=5*60).filter(exp_arrival__week_day=hour).filter(valid=True,exp_arrival__gte=datetime.date(2017,5,1)).count()
        ontime_average = samples_ontime / (samples_ontime + samples_delayed)
        print("Samples for day %d Ontime (less than 5 minutes delay): %.2f " % (day, ontime_average))

