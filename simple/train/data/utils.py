from data.models import Sample, Trip, Route
import csv
import datetime

def import_csvs(csv_files):
    results = []
    for csv_file in csv_files:
        before = Sample.objects.all().count()
        error = None
        try:
            import_csv(csv_file)
        except Exception, e:
            error = e
        after = Sample.objects.all().count()
        file_status = {'csv_file': csv_file,
                       'before': before,
                       'after': after,
                       'added': after - before,
                       'error': error}
        print file_status
        results.append(file_status)
    print '===================================================================='
    for ls in results:
        print '%-20s %s %s' % (ls['csv_file'], ls['added'], ls['error'])


def import_csv(csv_file):
    import os

    cmd = r"""\copy data_sample(train_num,
              start_date,
              trip_name,
              index,
              stop_id,
              stop_name,
              is_real_stop,
              valid,
              is_first,
              is_last,
              actual_arrival,
              exp_arrival,
              delay_arrival,
              actual_departure,
              exp_departure,
              delay_departure,
              data_file,
              data_file_line,
              data_file_link)
              from '%s' with delimiter ',' CSV HEADER""" % csv_file
    with open('/tmp/import.cmd', 'w') as fh:
        fh.write(' '.join(cmd.split()))
    os.system('cat /tmp/import.cmd | python manage.py dbshell')


def build_trips():
    """
    note: there is problem with sample with trip name 443_20140330
    since it has no real stops
    """
    from django.db import connection

    before = Trip.objects.count()
    with connection.cursor() as c:
        c.execute("""insert into data_trip(id,train_num,start_date,valid,stop_ids)
        (SELECT trip_name,train_num,start_date,valid,array_agg(stop_id ORDER BY index) AS stop_ids
            FROM public.data_sample
            WHERE is_real_stop and trip_id is null
            GROUP BY trip_name,train_num,start_date,valid)""")
        c.execute('update data_sample set trip_id = trip_name where trip_id is null')
    after = Trip.objects.count()
    print 'Before = %s After = %s Added = %s' % (before, after, after - before)


def benchit(func):
    def _wrap(*args, **kwargs):
        import time

        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print '%s took %.2f' % (func.__name__, t2 - t1)
        return result
    return _wrap


def csv_to_date(date_str):
    y,m,d = date_str.split('-')
    return datetime.date(year=int(y),month=int(m),day=int(d))

def csv_to_int(int_str):
    return int(int_str)

@benchit
def build_current_routes(csv_file):
    import collections
    stop_ids_by_trip = collections.defaultdict(list)
    found_routes = dict()
    with open(csv_file) as fh:
        reader = csv.DictReader(fh)
        for idx,row in enumerate(reader):
            if csv_to_bool(row['is_real_stop']):
                stop_ids_by_trip[row['trip_name']].append(row['stop_id'])
    route_id_by_trip = dict()
    for trip_name,stop_ids in stop_ids_by_trip.iteritems():
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
    print '=' * 50
    print 'Building Trips and Routes from csv file %s' % csv_file
    trip_names = set()
    trips = []
    route_id_by_trip = build_current_routes(csv_file)
    with open(csv_file) as fh:
        reader = csv.DictReader(fh)
        for idx,row in enumerate(reader):
            if row['trip_name'] not in trip_names:
                trip_data = {'id' : row['trip_name'],
                             'train_num' : int(row['train_num']),
                             'start_date': csv_to_date(row['start_date']),
                             'valid': csv_to_bool(row['valid']),
                             'route_id' : route_id_by_trip[row['trip_name']]
                             }
                trips.append(Trip(**trip_data))
                trip_names.add(row['trip_name'])
    print 'Found %s trips' % len(trips)
    Trip.objects.bulk_create(trips)
    print 'Built %s trips' % len(trips)



def csv_to_bool(b):
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
    import pytz
    if dt_str == '':
        return None
    # 2013-01-22T14:25:00+02:00
    dt_str2 = dt_str[-5:]
    dt_str1 = dt_str[:-6]
    dt = datetime.datetime.strptime(dt_str1,'%Y-%m-%dT%H:%M:%S')
    dt_il = pytz.timezone('Asia/Jerusalem').localize(dt)
    dt_utc = dt_il.astimezone(pytz.utc)
    return dt_utc

@benchit
def import_current_csv(csv_file):
    build_current_trips(csv_file)
    with open(csv_file) as fh:
        reader = csv.DictReader(fh)
        cur_samples = []
        for idx, row in enumerate(reader):
            s = Sample(trip_id=row['trip_name'],
                       index=csv_to_int(row['index']),
                       stop_id=csv_to_int(row['stop_id']),
                       stop_name=row['stop_name'],
                       is_real_stop=csv_to_bool(row['is_real_stop']),
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
                       data_file_line=csv_to_int(row['data_file_line']),
                       data_file_link=row['data_file_link'])
            cur_samples.append(s)
            if len(cur_samples) == 30000:
                Sample.objects.bulk_create(cur_samples)
                cur_samples = []
                print 'processes %s lines' % (idx+1)
        if cur_samples:
            Sample.objects.bulk_create(cur_samples)
            print 'processes %s lines' % (idx+1)

    print 'Read %s rows' % (1+idx)

@benchit
def gen_sql(csv_file):
    keys = ['train_num',
            'start_date',
            'trip_name',
            'index',
            'stop_id',
            'stop_name',
            'is_real_stop',
            'valid',
            'is_first',
            'is_last',
            'actual_arrival',
            'exp_arrival',
            'delay_arrival',
            'actual_departure',
            'exp_departure',
            'delay_departure',
            'data_file',
            'data_file_line',
            'data_file_link']
    keys_str = ','.join('"%s"' % k for k in keys)
    sql_file = csv_file.replace('.csv', '.sql')
    chunk_size = 10000
    build_current_trips(csv_file)

    with open(sql_file, 'w') as sh:
        with open(csv_file) as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader):
                if idx % chunk_size == 0:
                    sh.write('INSERT INTO data_sample(%s) VALUES ' % keys_str)
                values = ["'%s'" % row[k] if row[k] != '' else 'NULL' for k in keys]
                if idx % chunk_size > 0:
                    sh.write(',');
                sh.write('(%s)' % ','.join(values))
                if idx % chunk_size == chunk_size - 1:
                    sh.write(';\n')
                else:
                    sh.write('\n')
                if idx % 10000 == 0:
                    print 'Read %s rows' % (1+idx)
        sh.write(';\n')
    print 'Read %s rows' % (1+idx)


