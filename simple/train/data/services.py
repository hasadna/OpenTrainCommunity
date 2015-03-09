import json
import os
from django.conf import settings

STOPS = None

def read_json():
    import heb_stop_names
    global STOPS
    if STOPS:
        return
    STOPS = dict()
    trans_dict = read_translations()
    with open(os.path.join(settings.BASE_DIR,'data/stops.json')) as fh:
        stops = json.load(fh)
        for stop in stops:
            stop['stop_id'] = stop['gtfs_stop_id']
            hn = trans_dict.get(stop['stop_name'])
            stop['heb_stop_names'] = heb_stop_names.HEB_NAMES.get(stop['gtfs_stop_id'],[])
            if hn:
                stop['heb_stop_names'].append(hn)

            STOPS[stop['stop_id']] = stop


def csv_to_dicts(csv_file):
    """ csv_file can be file hander or string """
    import csv
    result = []
    with open(csv_file) as fh:
        reader = csv.DictReader(fh, delimiter=',')
        for row in reader:
            for k in row.keys():
                if row[k] is None:
                    row[k] = ''
                else:
                    row[k] = row[k].decode('utf-8-sig', 'ignore')
            result.append(row)
        new_result = []
        for row in result:
            new_row = dict()
            for k,v in row.iteritems():
                new_row[k.decode('utf-8-sig')] = v
            new_result.append(new_row)
        assert len(new_result) == len(result)
    return new_result

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
    return defval or unicode(stop_id)

def get_stops():
    read_json()
    global STOPS
    return STOPS.values()[:]

def get_stop(stop_id):
    global STOPS
    read_json()
    return STOPS[stop_id].copy()

