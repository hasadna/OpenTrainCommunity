from data.models import Sample, Trip, Route, Service
import csv
import datetime
from collections import namedtuple
from data import cache_utils
from django.db import transaction
import pytz

IST = pytz.timezone('Asia/Jerusalem')

def benchit(func):
    def _wrap(*args, **kwargs):
        import time

        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print('%s took %.2f' % (func.__name__, t2 - t1))
        return result
    return _wrap


def csv_to_date(date_str):
    y,m,d = date_str.split('-')
    return datetime.date(year=int(y),month=int(m),day=int(d))

def csv_to_int(int_str,allow_none=False):
    if allow_none and (int_str == '' or int_str is None):
        return None
    return int(int_str)

@benchit
def build_current_routes(csv_file):
    import collections
    stop_ids_by_trip = collections.OrderedDict()
    found_routes = dict()
    with open(csv_file,encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for idx,row in enumerate(reader):
            if csv_to_bool(row['is_real_stop']):
                if row['trip_name'] not in stop_ids_by_trip:
                    stop_ids_by_trip[row['trip_name']] = []
                stop_ids_by_trip[row['trip_name']].append(int(row['stop_id']))
    route_id_by_trip = dict()
    for trip_name,stop_ids in stop_ids_by_trip.items():
        tuple_stop_ids = tuple(stop_ids)
        if tuple_stop_ids in found_routes:
            route_id = found_routes[tuple_stop_ids]
            route_id_by_trip[trip_name] = route_id
        else:
            r,_ = Route.objects.get_or_create(stop_ids=stop_ids)
            route_id_by_trip[trip_name] = r.id
            found_routes[tuple_stop_ids] = r.id
    return route_id_by_trip

@benchit
def build_current_trips(csv_file):
    print('=' * 50)
    print('Building Trips and Routes from csv file %s' % csv_file)
    trip_names = set()
    trips = []
    route_id_by_trip = build_current_routes(csv_file)
    with open(csv_file,encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for idx,row in enumerate(reader):
            start_date = csv_to_date(row['start_date'])
            if row['trip_name'] not in trip_names:
                trip_data = {'id' : row['trip_name'],
                             'train_num' : int(row['train_num']),
                             'start_date': start_date,
                             'x_week_day_local': start_date.isoweekday() % 7, #isoweekday is 1..7
                             'valid': csv_to_bool(row['valid']),
                             'route_id' : route_id_by_trip[row['trip_name']]
                             }
                trips.append(Trip(**trip_data))
                trip_names.add(row['trip_name'])
    print('Found %s trips' % len(trips))
    Trip.objects.bulk_create(trips)
    print('Built %s trips' % len(trips))



def csv_to_bool(b):
    if b is None:
        return None
    if int(b) == 1:
        return True
    if int(b) == 0:
        return False
    assert False,'illegal b = %s' % b

def csv_to_float(b):
    if b == '':
        return None
    return float(b)

def csv_to_datetime(dt_str):
    if dt_str == '':
        return None
    # 2013-01-22T14:25:00+02:00
    dt_str2 = dt_str[-5:]
    dt_str1 = dt_str[:-6]
    dt = datetime.datetime.strptime(dt_str1,'%Y-%m-%dT%H:%M:%S')
    dt_il = IST.localize(dt)
    dt_utc = dt_il.astimezone(pytz.utc)
    return dt_utc


@benchit
@transaction.atomic
def import_current_csv(csv_file):
    build_current_trips(csv_file)
    with open(csv_file, encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        cur_samples = []
        for idx, row in enumerate(reader):
            is_real_stop=csv_to_bool(row['is_real_stop'])
            if not is_real_stop:
                continue
            s = Sample(trip_id=row['trip_name'],
                       is_skipped=False, # to be updated later
                       index=csv_to_int(row['index']),
                       stop_id=csv_to_int(row['stop_id']),
                       valid=csv_to_bool(row['valid']),
                       is_first=csv_to_bool(row['is_first']),
                       is_last=csv_to_bool(row['is_last']),
                       actual_arrival=csv_to_datetime(row['actual_arrival']),
                       actual_departure=csv_to_datetime(row['actual_departure']),
                       exp_arrival=csv_to_datetime(row['exp_arrival']),
                       exp_departure=csv_to_datetime(row['exp_departure']),
                       delay_departure=csv_to_float(row['delay_departure']),
                       delay_arrival=csv_to_float(row['delay_arrival']),
                       data_file=row['data_file'],
                       data_file_line=csv_to_int(row['data_file_line'],allow_none=True),
                       is_planned=csv_to_bool(row.get('is_planned')),
                       is_stopped=csv_to_bool(row.get('is_stopped')),
                       version=csv_to_bool(row.get('version',1)))

            if s.is_first and s.valid:
                t = Trip.objects.get(pk=s.trip_id)
                t.x_hour_local = s.exp_departure.astimezone(IST).hour
                t.save(update_fields=['x_hour_local'])
            cur_samples.append(s)
            if len(cur_samples) == 30000:
                Sample.objects.bulk_create(cur_samples)
                cur_samples = []
                print('processes %s lines' % (idx+1))
        if cur_samples:
            Sample.objects.bulk_create(cur_samples)
            print('processes %s lines' % (idx+1))
    print('Read %s rows' % (1+idx))
    fix_x_time()


def fix_x_time():
    trips = list(Trip.objects.filter(x_hour_local__isnull=True))
    print('Fix missing hour for %s trips' % len(trips))
    for idx, t in enumerate(trips):
        if idx % 100 == 0:
            print('{0}/{1} completed'.format(idx, len(trips)))
        t.fix_x_hour_local()


def build_all_services():
    print('In build_all_services')
    routes = Route.objects.all()
    print('Found %s routes' % len(routes))
    for idx,route in enumerate(routes):
        route.group_into_services()
        if (1+idx) % 10 == 0:
            print('Completed %s/%s routes' % (idx+1,len(routes)))
    check_services()


def check_services():
    from django.db.models import Count
    count = Trip.objects.count()
    trips = Trip.objects.all().annotate(service_count=Count('service'))
    for idx,trip in enumerate(trips):
        if trip.valid:
            assert trip.service_count == 1,'Trip %s has more than one service' % trip.id
        else:
            assert trip.service_count == 0,'Trip %s is not valid but has services' % trip.id
        if (1+idx)%100 == 0:
            print('Completed %s/%s trips' % (idx+1,count))

ServicesResult = namedtuple('ServicesResult',['bad','unreliable','good'])


def _analyze_services_impl():
    services = list(Service.objects.all())
    print('Found %s services' % len(services))
    bad_services = []
    unreliable_services = []
    good_services = []
    for idx,service in enumerate(services):
        skipped_stop_ids = service.get_skipped_stop_ids()
        if service.trips.count() <= 2:
            unreliable_services.append(service.id)
        elif len(skipped_stop_ids) > 0:
            bad_services.append(service.id)
        else:
            good_services.append(service.id)
    return {'bad':bad_services,
            'good':good_services,
            'unreliable':unreliable_services}

def analyze_services():
    d = _analyze_services_impl()
    return ServicesResult(bad=Service.objects.filter(id__in=d['bad']),
                          unreliable=Service.objects.filter(id__in=d['unreliable']),
                          good=Service.objects.filter(id__in=d['good']))

@transaction.atomic
def remove_skip_stops():
    print('Removing Skipped Stops')
    sr = analyze_services()
    route_ids = {s.route_id for s in sr.bad}
    #bad_routes = Route.objects.filter(id__in=route_ids)
    print('bad_services: %s' % len(sr.bad))
    print('unreliable_services : %s' % len(sr.unreliable))
    print('good_services: %s' % len(sr.good))
    print('bad routes: %s' % (len(route_ids)))
    print('# of routes before: %s' % Route.objects.count())
    for idx,service in enumerate(sr.bad):
        service.remove_skip_stops()
        if (idx + 1 % 100 == 0):
            print('%s/%s completed' % (1+idx,len(sr.bad)))
    print('# of routes after: %s' % Route.objects.count())





