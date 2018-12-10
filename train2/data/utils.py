import calendar
import datetime
import time
import logging

import re

from math import radians, cos, sin, asin, sqrt


def date_to_millis_since_epoch(date):
    if date is None:
        return None

    assert isinstance(date, (datetime.datetime, datetime.date)), date

    if hasattr(date, 'utcoffset') and date.utcoffset:
        date -= date.utcoffset() or 0

    millis = int(calendar.timegm(date.timetuple()) * 1000)
    return millis


def parse_date(dt_str, reverse=False):
    if dt_str is None:
        return None

    if dt_str.isdigit():
        timestamp = int(dt_str)
        if timestamp > 1e12:  # java time, with milliseconds
            timestamp /= 1000
        return datetime.datetime.fromtimestamp(timestamp)

    try:
        if reverse:
            y, m, d = [int(x) for x in re.split("[-/]",dt_str)]
        else:
            d, m, y = [int(x) for x in re.split("[-/]",dt_str)]
        if y < 2013:
            raise ValueError('Wrong year %s for param %s' % (y, dt_str))
        return datetime.datetime(year=y, month=m, day=d)
    except ValueError as e:
        raise ValueError('Wrong date param %s: %s' % (dt_str, str(e)))

def benchit(func):
    def wrap(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print('%s took %.2f' % (func.__name__, t2 - t1))
        return result

    return wrap


def haversine(latlon1, latlon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km*1000


def is_list_in_list(lst1, lst2):
    # return True if you can get lst1 by removing elements
    # from lst2, without any shuffling
    if len(lst1) > len(lst2):
        return False
    index1 = 0
    index2 = 0
    while True:
        if lst1[index1] == lst2[index2]:
            index1 += 1
            index2 += 1
        else:
            index2 += 1
        if index1 == len(lst1):
            return True
        if index2 == len(lst2):
            return False

