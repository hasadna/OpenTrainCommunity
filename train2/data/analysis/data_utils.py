import os
import sys
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE', 'train2.settings.dev_settings')
import datetime
import django
django.setup()

# start postgres server on mac:
# postgres -D /usr/local/var/postgres

from data import models
from collections import OrderedDict, namedtuple

GeoLoc = namedtuple('GeoLoc', ['lat', 'lon'])


def get_samples(date1, date2, max_samples=10**9):
    res = models.Sample.objects.filter(exp_arrival__gte=date1).filter(exp_arrival__lte=date2)[:max_samples]
    res = list(res)

    return res


def get_samples_by_trip(date1, date2, max_samples=10**9):
    trips = models.Trip.objects.filter(date__gte=date1).filter(date__lte=date2)[:max_samples]
    res = OrderedDict()
    for trip in trips:
        res[trip.id] = trip.samples.all()

    return res

### ---------------------------------------------------------------------------------------------------------------------------------------

def get_name_by_id(id):
    stop = list(models.Stop.objects.filter(gtfs_stop_id=id))
    if len(stop) != 1:
        raise AssertionError('Problem with id to name in stop %d' % id)
    else:
        name = stop[0].english

    return name

def get_loc_by_id(id):
    stop = list(models.Stop.objects.filter(gtfs_stop_id=id))
    if len(stop) != 1:
        raise AssertionError('Problem with id to name in stop %d' % id)
    else:
        loc = GeoLoc(lat=stop[0].lat, lon=stop[0].lon)

    return loc

### ---------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    name = get_name_by_id(700)
    loc = get_loc_by_id(700)
    date1 = datetime.datetime(2015, 5, 15)
    date2 = datetime.datetime(2015, 5, 16)
    # samples = get_samples(date1, date2)
    # get_trips = models.Trip.objects.filter(id='100_20130101')
    get_trips = get_samples_by_trip(date1, date2)

    print("Finished!")

