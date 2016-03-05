from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import logging
import data.stop_utils
from django.utils.translation import activate

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        data.stop_utils.build_stops()
        LOGGER.info("done build stops")