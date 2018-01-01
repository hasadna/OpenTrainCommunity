import calendar
import datetime
import json
import logging

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import activate

from data.models import Trip

logger = logging.getLogger(__name__)

TRIP_FIELDS = [
    'x_avg_delay_arrival',
    'x_before_last_delay_arrival',
    'x_hour_local',
    'x_last_delay_arrival',
    'x_max2_delay_arrival',
    'x_max_delay_arrival',
    'x_week_day_local'
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--month', type=int, required=True)
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument('--output', type=str, required=True)
        parser.add_argument('--indent', type=int)

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        y = options['year']
        m = options['month']
        wd, num_days = calendar.monthrange(y, m)
        trips = Trip.objects.filter(valid=True,
                                    date__gte=datetime.date(y, m, 1),
                                    date__lte=datetime.date(y, m, num_days)).order_by('date')
        with open(options['output'], "w") as fh:
            json.dump(list(self.get_trips_json(trips)),
                      fh,
                      indent=options['indent'])

        logger.info("Wrote to file %s", options['output'])

    def get_trips_json(self, trips):
        for t in trips:
            yield self.to_json(t)

    def to_json(self, t):
        result = {
            'id': t.id,
            'date': t.date.strftime("%Y-%m-%d"),
        }
        for f in TRIP_FIELDS:
            result[f] = getattr(t, f)
        return result