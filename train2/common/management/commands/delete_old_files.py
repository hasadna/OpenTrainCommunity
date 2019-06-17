import os
import logging
import re

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone


NAME_PAT = re.compile(r'^(\d{4})\-(\d{2})\-(\d{2})$')

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        base_dir = os.path.join(settings.BASE_DIR, 'common', 'gtfs_workdir')
        files = os.listdir(base_dir)
        for f in files:
            print(f)
            full_path = os.path.join(base_dir, f)
            m = NAME_PAT.match(f)
            if not m:
                continue
            if os.path.isdir(full_path):
                logger.info("%s is directory", full_path)
            y, m, d = NAME_PAT.groups()

