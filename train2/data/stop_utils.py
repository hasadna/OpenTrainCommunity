import json
import logging

import os
from django.conf import settings

from . import heb_stop_names
from . import models

LOGGER = logging.getLogger(__name__)


def build_stops():
    with open(os.path.join(settings.BASE_DIR, 'data/stops.json')) as fh:
        stops = json.load(fh)
    for sj in stops:
        try:
            stop = models.Stop.objects.get(gtfs_stop_id=sj['gtfs_stop_id'])
            created = False
        except models.Stop.DoesNotExist:
            stop = models.Stop.objects.create(gtfs_stop_id=sj['gtfs_stop_id'],
                                              lat=sj['latlon'][0],
                                              lon=sj['latlon'][1],
                                              english=sj['stop_name'],
                                              hebrews=[sj['stop_short_name']]
                                              )
            created = True

        names = heb_stop_names.HEB_NAMES.get(stop.gtfs_stop_id) or []
        if sj['stop_short_name'] not in names:
            names.append(sj['stop_short_name'])
        if names != stop.hebrews:
            stop.hebrews = names
            stop.save()
        if created:
            LOGGER.info("Built stop %s", stop)
        else:
            LOGGER.info("stop %s already built", stop)
