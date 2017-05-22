from django.core.management.base import BaseCommand, CommandError
from data import check_data

import logging

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
  def handle(self, *args, **options):
    check_data.run()
    LOGGER.info("Check is complete") 


