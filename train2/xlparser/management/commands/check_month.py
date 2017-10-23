from django.core.management.base import BaseCommand, CommandError
from data import check_data

import logging
import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("month", type=int, choices=range(1,13), help="month")
        parser.add_argument("year", type=int, choices=range(2017, datetime.datetime.now().year + 1), help="year")

    def handle(self, *args, **options):
        logger.info('%d %d',options['month'], options['year'])
        check_data.run_month(options['year'],
                         options['month'])
        logger.info("Check is complete")



