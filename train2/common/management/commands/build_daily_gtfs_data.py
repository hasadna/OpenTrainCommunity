import datetime
import logging
from django.core.management import BaseCommand
from ...ot_gtfs_utils import get_or_create_daily_trips
from ...slack_utils import send_message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--force', action='store_true', default=False, help="force build")
        parser.add_argument('--date', required=False, help='YYYY-MM-DD')

    def handle(self, *args, **kwargs):
        try:
            if kwargs['date']:
                date = datetime.date(*[int(x) for x in kwargs['date'].split("-")])
            else:
                date = datetime.date.today()
            logger.info("Started build_daily_gtfs_commands for date %s", date)
            daily = get_or_create_daily_trips(date, force=kwargs['force'])
            logger.info("End build_daily_gtfs_commands shape = %s", daily.shape)
            send_message(f'build_daily_gtfs_commands ended successfully daily = {daily.shape}')
        except Exception as ex:
            logger.exception(ex)
            send_message(f'Failed in build_daily_gtfs_commands {ex}')

