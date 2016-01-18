import datetime
import functools
import time
from collections import namedtuple

import django.db
from django.conf import settings

from . import errors
from .models import Route

Filters = namedtuple('Filters', ['from_date', 'to_date'])


def benchit(func):
    def wrap(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print('%s took %.2f' % (func.__name__, t2 - t1))
        return result

    return wrap


WEEK_DAYS = [1, 2, 3, 4, 5, 6, 7]

HOURS = [(4, 7),
         (7, 9),
         (9, 12),
         (12, 15),
         (15, 18),
         (18, 21),
         (21, 24),
         (24, 28),
         ]


def _check_hours():
    for idx, (h1, h2) in enumerate(HOURS):
        assert isinstance(h1, int)
        assert isinstance(h2, int)
        if idx > 0:
            assert h1 == HOURS[idx - 1][1]


_check_hours()


def parse_date(dt_str):
    if dt_str is None:
        return None

    if dt_str.isdigit():
        timestamp = int(dt_str)
        if timestamp > 1e12:  # java time, with milliseconds
            timestamp = timestamp / 1000
        return datetime.datetime.fromtimestamp(timestamp)

    try:
        d, m, y = [int(x) for x in dt_str.split('/')]
        if y < 2013:
            raise errors.InputError('Wrong year %s for param %s' % (y, dt_str))
        return datetime.date(year=y, month=m, day=d)
    except ValueError as e:
        raise errors.InputError('Wrong date param %s: %s' % (dt_str, str(e)))


def encode_date(date):
    import calendar
    if date is None:
        return None

    assert isinstance(date, (datetime.datetime, datetime.date)), date

    if hasattr(date, 'utcoffset') and date.utcoffset:
        date -= date.utcoffset() or 0

    millis = int(calendar.timegm(date.timetuple()) * 1000)
    return millis


def get_route_info_full(route_id, from_date, to_date):
    filters = Filters(from_date=from_date, to_date=to_date)
    route = Route.objects.get(id=route_id)
    table = _get_stats_table(route=route, filters=filters)
    stats = _complete_table(table, route.stop_ids)
    stats.sort(key=_get_info_sort_key)
    return stats


def get_path_info_full(origin_id, destination_id, from_date, to_date):
    routes = get_routes_from_to(origin_id, destination_id)
    filters = Filters(from_date=from_date, to_date=to_date)
    table = _get_stats_table(routes=routes, filters=filters,origin_id=origin_id, destination_id=destination_id)
    stats = _complete_table(table, [origin_id, destination_id])
    stats.sort(key=_get_info_sort_key)
    return stats


def get_routes_from_to(origin_id, destination_id):
    result = []
    for route in Route.objects.all():
        try:
            idx1 = route.stop_ids.index(origin_id)
            idx2 = route.stop_ids.index(destination_id)
        except ValueError:
            pass
        else:
            if idx1 < idx2:
                result.append(route)
    return result


def _get_info_sort_key(stat):
    info = stat['info']
    hours = info['hours'] if info['hours'] != 'all' else [1000, 1000]
    week_day = info['week_day'] if info['week_day'] != 'all' else 1000
    return week_day, hours

    return stats


def _find_relevant_entries(table, week_day, hours):
    result = []
    for entry in table:
        if hours != 'all':
            hours_range = [h % 24 for h in range(hours[0], hours[1])]
        if week_day == 'all' or entry['week_day_local'] == week_day - 1:
            if hours == 'all' or entry['hour_local'] in hours_range:
                result.append(entry)
    return result


def _avg_entries(stop_id, entries):
    result = dict()
    keys = ["arrival_on_time_pct",
            "arrival_late_pct",
            "departure_early_pct",
            "departure_on_time_pct",
            "arrival_early_pct",
            "departure_late_pct"]
    result['stop_id'] = stop_id
    total_num = sum(e.get('num_trips', 0) for e in entries)
    for key in keys:
        if total_num != 0:
            count_key = key.replace('_pct', '_count')
            sum_values = sum(entry.get(count_key, 0) for entry in entries)
            result[key] = 1.0 * sum_values / total_num
        else:
            result[key] = 0
    return result


def _complete_table(table, stop_ids):
    result = []
    for week_day in WEEK_DAYS + ['all']:
        for hours in HOURS + ['all']:
            entries = _find_relevant_entries(table, week_day, hours)
            stops = []
            num_trips = None
            for stop_id in stop_ids:
                stop_id_entries = [entry for entry in entries if entry['stop_id'] == stop_id]
                prev_num_trips = num_trips
                num_trips = sum(e['num_trips'] for e in stop_id_entries)
                if prev_num_trips is not None:
                    assert num_trips == prev_num_trips, 'inconsistency in num trips'
                if num_trips == 0:
                    stops.append({})
                else:
                    stops.append(_avg_entries(stop_id, stop_id_entries))
            stat = {
                'info': {
                    'num_trips': num_trips or 0,
                    'week_day': week_day,
                    'hours': list(hours) if isinstance(hours, tuple) else hours
                },
                'stops': stops
            }
            result.append(stat)
    return result


@functools.lru_cache()
def get_service_stat(service):
    if settings.USE_SQLITE3:
        select_stmt = '''
            SELECT s.stop_id as stop_id,
            count(s.stop_id) as num_trips,
            avg(s.delay_arrival) as avg_delay_arrival,
            avg(s.delay_departure) as avg_delay_departure,
            avg(strftime('%%s',s.actual_departure) - strftime('%%s',s.actual_arrival)) as time_in_stop
            FROM
            data_sample as s
            where s.trip_id in %(trip_ids_str)s
            GROUP by s.stop_id
        '''
    else:
        select_stmt = '''
            SELECT s.stop_id as stop_id,
            count(s.stop_id) as num_trips,
            avg(s.delay_arrival) as avg_delay_arrival,
            avg(s.delay_departure) as avg_delay_departure,
            avg(s.actual_departure-s.actual_arrival) as time_in_stop
            FROM
            data_sample as s
            where s.trip_id in %(trip_ids_str)s
            GROUP by s.stop_id
        '''
    trip_ids = list(service.trips.all().values_list('id', flat=True))
    trip_ids_str = '({0})'.format(','.join(("'{0}'".format(tid) for tid in trip_ids)))
    select_kwargs = {'trip_ids_str': trip_ids_str}
    cursor = django.db.connection.cursor()
    cursor.execute(select_stmt % select_kwargs)
    cols = ['stop_id', 'num_trips', 'avg_delay_arrival', 'avg_delay_departure', 'time_in_stop']
    result = []
    for row in cursor:
        row_dict = dict(zip(cols, row))
        ts = row_dict['time_in_stop']
        if ts is not None:
            if not settings.USE_SQLITE3:
                ts = ts.total_seconds()  # in postgres: timedelta object
        row_dict['time_in_stop'] = ts
        result.append(row_dict)
    return result


def _get_select_postgres(*, route, filters, early_threshold, late_threshold):
    select_stmt = ('''
        SELECT  count(s.stop_id) as num_trips,
                s.stop_id as stop_id,
                t.x_week_day_local as week_day_local,
                t.x_hour_local as hour_local,
                sum(case when s.delay_arrival <= %(early_threshold)s then 1 else 0 end) as arrival_early_count,
                sum(case when s.delay_arrival > %(early_threshold)s and s.delay_arrival < %(late_threshold)s then 1 else 0 end) as arrival_on_time_count,
                sum(case when s.delay_arrival >= %(late_threshold)s then 1 else 0 end) as arrival_late_count,

                sum(case when s.delay_departure <= %(early_threshold)s then 1 else 0 end) as departure_early_count,
                sum(case when s.delay_departure > %(early_threshold)s and s.delay_departure < %(late_threshold)s then 1 else 0 end) as departure_on_time_count,
                sum(case when s.delay_departure >= %(late_threshold)s then 1 else 0 end) as departure_late_count

        FROM
        data_route as r,
        data_trip as t,
        data_sample as s

        WHERE
        r.id = %(route_id)s
        AND t.route_id = r.id
        AND t.valid
        AND s.trip_id = t.id
        ''' +
                   (' AND t.start_date >= %(start_date)s' if filters.from_date else '')
                   +
                   (' AND t.start_date <= %(to_date)s' if filters.to_date else '')
                   +
                   '''
                       GROUP BY s.stop_id,week_day_local,hour_local
                   ''')
    select_kwargs = {
        'route_id': route.id,
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': route.stop_ids,
        'start_date': filters.from_date,
        'to_date': filters.to_date
    }
    return select_stmt, select_kwargs


def _get_select_from_to_postgres(*, routes, filters, origin_id, destination_id, early_threshold, late_threshold):
    route_ids = [r.id for r in routes]
    select_stmt = ('''
        SELECT  count(s.stop_id) as num_trips,
                s.stop_id as stop_id,
                t.x_week_day_local as week_day_local,
                t.x_hour_local as hour_local,
                sum(case when s.delay_arrival <= %(early_threshold)s then 1 else 0 end) as arrival_early_count,
                sum(case when s.delay_arrival > %(early_threshold)s and s.delay_arrival < %(late_threshold)s then 1 else 0 end) as arrival_on_time_count,
                sum(case when s.delay_arrival >= %(late_threshold)s then 1 else 0 end) as arrival_late_count,

                sum(case when s.delay_departure <= %(early_threshold)s then 1 else 0 end) as departure_early_count,
                sum(case when s.delay_departure > %(early_threshold)s and s.delay_departure < %(late_threshold)s then 1 else 0 end) as departure_on_time_count,
                sum(case when s.delay_departure >= %(late_threshold)s then 1 else 0 end) as departure_late_count

        FROM
        data_route as r,
        data_trip as t,
        data_sample as s

        WHERE
        r.id =  ANY(%(route_ids)s)
        AND t.route_id = r.id
        AND t.valid
        AND s.trip_id = t.id
        ''' +
                   (' AND t.start_date >= %(start_date)s' if filters.from_date else '')
                   +
                   (' AND t.start_date <= %(to_date)s' if filters.to_date else '')
                   +
                   '''
                       GROUP BY s.stop_id,week_day_local,hour_local
                   ''')
    select_kwargs = {
        'route_ids': route_ids,
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': [origin_id, destination_id],
        'start_date': filters.from_date,
        'to_date': filters.to_date
    }
    return select_stmt, select_kwargs



def _get_select_sqlite3(*, route, filters, early_threshold, late_threshold):
    select_stmt = ('''
        SELECT  count(s.stop_id) as num_trips,
                s.stop_id as stop_id,
                t.x_week_day_local as week_day_local,
                t.x_hour_local as hour_local,
                sum(case when s.delay_arrival <= %(early_threshold)s then 1 else 0 end) as arrival_early_count,
                sum(case when s.delay_arrival > %(early_threshold)s and s.delay_arrival < %(late_threshold)s then 1 else 0 end) as arrival_on_time_count,
                sum(case when s.delay_arrival >= %(late_threshold)s then 1 else 0 end) as arrival_late_count,

                sum(case when s.delay_departure <= %(early_threshold)s then 1 else 0 end) as departure_early_count,
                sum(case when s.delay_departure > %(early_threshold)s and s.delay_departure < %(late_threshold)s then 1 else 0 end) as departure_on_time_count,
                sum(case when s.delay_departure >= %(late_threshold)s then 1 else 0 end) as departure_late_count

        FROM
        data_route as r,
        data_trip as t,
        data_sample as s

        WHERE
        r.id = %(route_id)s
        AND t.route_id = r.id
        AND t.valid
        AND s.trip_id = t.id
        ''' +
                   (''' AND t.start_date >= datetime('%(start_date)s')''' if filters.from_date else '')
                   +
                   (''' AND t.start_date <= datetime('%(to_date)s')''' if filters.to_date else '')
                   +
                   '''
                       GROUP BY s.stop_id,week_day_local,hour_local
                   ''')
    select_kwargs = {
        'route_id': route.id,
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': route.stop_ids,
        'start_date': filters.from_date,
        'to_date': filters.to_date
    }
    return select_stmt % select_kwargs, {}


@benchit
def _get_stats_table(*, route=None,
                     routes=None,
                     origin_id=None,
                     destination_id=None,
                     filters=None):
    assert (route is None) ^ (routes is None), 'exactly one of route, routes must be None'
    early_threshold = -120
    late_threshold = 300
    if route:
        if settings.USE_SQLITE3:
            select_stmt, select_kwargs = _get_select_sqlite3(route=route, filters=filters,
                                                             early_threshold=early_threshold,
                                                             late_threshold=late_threshold)
        else:
            select_stmt, select_kwargs = _get_select_postgres(route=route, filters=filters,
                                                              early_threshold=early_threshold,
                                                              late_threshold=late_threshold)
    else:
        if settings.USE_SQLITE3:
            assert False, 'not implemented for sqlite3 yet'
            select_stmt, select_kwargs = _get_select_from_to_sqlite3(routes=routes,
                                                                     filters=filters,
                                                                     origin_id=origin_id,
                                                                     destination_id=destination_id,
                                                                     early_threshold=early_threshold,
                                                                     late_threshold=late_threshold)
        else:
            select_stmt, select_kwargs = _get_select_from_to_postgres(routes=routes,
                                                                      filters=filters,
                                                                      origin_id=origin_id,
                                                                      destination_id=destination_id,
                                                                      early_threshold=early_threshold,
                                                                      late_threshold=late_threshold)

    cursor = django.db.connection.cursor()
    cursor.execute(select_stmt, select_kwargs)

    cols = [
        'num_trips',
        'stop_id',
        'week_day_local',
        'hour_local',
        'arrival_early_count',
        'arrival_on_time_count',
        'arrival_late_count',
        'departure_early_count',
        'departure_on_time_count',
        'departure_late_count',
    ]

    result = []
    for row in cursor:
        stat = dict(zip(cols, row))
        result.append(stat)
    return result
