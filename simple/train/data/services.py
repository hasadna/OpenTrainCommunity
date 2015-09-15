import json
import os
from django.conf import settings

STOPS = None

def read_json():
    from . import heb_stop_names
    global STOPS
    if STOPS:
        return
    STOPS = dict()
    trans_dict = read_translations()
    with open(os.path.join(settings.BASE_DIR,'data/stops.json')) as fh:
        stops = json.load(fh)
        for stop in stops:
            stop['stop_id'] = stop['gtfs_stop_id']
            heb_names = heb_stop_names.HEB_NAMES.get(stop['gtfs_stop_id'],[])
            hn = trans_dict.get(stop['stop_name'])
            if hn and hn not in heb_names:
                heb_names.append(hn)
            stop['heb_stop_names'] = heb_names
            STOPS[stop['stop_id']] = stop


def csv_to_dicts(csv_file):
    """ csv_file can be file hander or string """
    import csv
    with open(csv_file) as fh:
        reader = csv.DictReader(fh, delimiter=',')
        result = []
        for row in reader:
            new_row = dict()
            for k, v in row.items():
                try:
                    k = k.encode('utf-8').decode('utf-8-sig')
                    k = k.rstrip('\uefff')
                except Exception as e:
                    print(e)
                new_row[k] = v
            result.append(new_row)
    return result


def read_translations():
    trans_he = dict()
    rows = csv_to_dicts(os.path.join(settings.BASE_DIR,'data/translations.txt'))
    for row in rows:
        if row['lang'] == 'HE':
            trans_he[row['trans_id']] = row['translation']
    return trans_he


def get_stop_name(stop_id,defval=None):
    global STOPS
    read_json()
    if stop_id in STOPS:
        return STOPS[stop_id]['stop_name']
    return defval or str(stop_id)

def get_heb_stop_name(stop_id,defval=None):
    global STOPS
    read_json()
    if stop_id in STOPS:
        return STOPS[stop_id]['heb_stop_names'][0]
    return defval or str(stop_id)

def get_stops(stop_ids=None):
    read_json()
    global STOPS
    if stop_ids is None:
        return list(STOPS.values())
    return [STOPS[stop_id] for stop_id in stop_ids]


def get_stop(stop_id):
    global STOPS
    read_json()
    return STOPS[stop_id].copy()

