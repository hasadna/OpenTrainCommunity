from django.core.management.base import BaseCommand, CommandError
import xlparser.utils_2015
import logging


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        files = options['files']
        ok = []
        bad = []
        for f in files:
            LOGGER.info('starting parse %s',f)
            try:
                xlparser.utils_2015.parse_xl(f)
                ok.append(f)
            except Exception as e:
                LOGGER.exception(e)
                bad.append((f,e))
            LOGGER.info('end parse %s',f)

        if bad:
            for f,e in bad:
                LOGGER.error("failed in %s with %s", f,e)
        else:
            LOGGER.info("ALL %s files were parsed ok", len(ok))
        LOGGER.info("REMEMBER TO RUN python manage.py prep_x_fields")
