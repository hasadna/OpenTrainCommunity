import json
import os
from django.conf import settings

STOPS = None

def read_json():
    global STOPS
    if STOPS:
        return
    STOPS = dict()
    with open(os.path.join(settings.BASE_DIR,'data/stops.json')) as fh:
        stops = json.load(fh)
        for stop in stops:
            stop['stop_id'] = stop['gtfs_stop_id']
            STOPS[stop['stop_id']] = stop

def get_stop_name(stop_id,defval=None):
    global STOPS
    read_json()
    if stop_id in STOPS:
        return STOPS[stop_id]['stop_name']
    return defval or unicode(stop_id)

def get_stops():
    read_json()
    global STOPS
    return STOPS.values()[:]

def get_stop(stop_id):
    global STOPS
    read_json()
    return STOPS[stop_id].copy()

