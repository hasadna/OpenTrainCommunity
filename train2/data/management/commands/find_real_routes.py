import calendar
import datetime

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import activate

import data.logic

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--month', type=int)
        parser.add_argument('--year', type=int)
    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        y = options['year']
        m = options['month']
        wd,num_days = calendar.monthrange(y, m)
        data.logic.find_real_routes(from_date=datetime.date(y,m,1),
                                    to_date=datetime.date(y,m,num_days))

