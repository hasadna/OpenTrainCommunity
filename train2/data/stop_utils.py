import json
import logging

import os
from django.conf import settings

from . import models

LOGGER = logging.getLogger(__name__)


def build_stops():
    with open(os.path.join(settings.BASE_DIR, 'data/stops.json')) as fh:
        stops = json.load(fh)
    for stop in stops:
        stop, created = models.Stop.objects.get_or_create(gtfs_stop_id=stop['gtfs_stop_id'],
                                                          lat=stop['latlon'][0],
                                                          lon=stop['latlon'][1],
                                                          english=stop['stop_name'],
                                                          hebrews=[stop['stop_short_name']]
                                                          )
        if created:
            LOGGER.info("Built stop %s", stop)
        else:
            LOGGER.info("stop %s already built", stop)
