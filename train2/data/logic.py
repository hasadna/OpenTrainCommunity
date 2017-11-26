import logging

from collections import namedtuple
from functools import cmp_to_key

import django.db
from django.db.models import Count

from . import utils
from .models import Route, Trip, Sample

logger = logging.getLogger(__name__)

Filters = namedtuple('Filters', ['from_date', 'to_date'])

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


def get_stops_from_to(origin_id, destination_id):
    """
    :param origin_id: return list of all stop ids between origin_id to destination_id
    :param destination_id:
    :return:
    """
    routes = get_routes_from_to(origin_id, destination_id)
    all_stop_ids = set()
    for r in routes:
        idx1 = r.stop_ids.index(origin_id)
        idx2 = r.stop_ids.index(destination_id)
        cur_stop_ids = r.stop_ids[idx1:idx2+1]
        all_stop_ids |= set(cur_stop_ids)
    all_stop_ids = list(all_stop_ids)

    def cmp_stop_ids(stop1, stop2):
        for r in routes:
            try:
                idx_stop1 = r.stop_ids.index(stop1)
                idx_stop2 = r.stop_ids.index(stop2)
                if idx_stop1 == idx_stop2:
                    return 0
                return (idx_stop1 - idx_stop2) // abs(idx_stop1 - idx_stop2)
            except ValueError:
                pass
        return 0 # they don't share any path - consider them as equal

    return sorted(all_stop_ids,key=cmp_to_key(cmp_stop_ids))


def get_route_info_full(route_id, from_date, to_date):
    filters = Filters(from_date=from_date, to_date=to_date)
    route = Route.objects.get(id=route_id)
    table = _get_stats_table(route=route, filters=filters)
    stats = _complete_table(table, route.stop_ids)
    stats.sort(key=_get_info_sort_key)
    return stats


def get_from_to_info_full(*, origin_id,
                          destination_id,
                          from_date,
                          to_date,
                          skipped_ids,
                          skipped_complement):
    routes = get_routes_from_to(origin_id, destination_id, skipped_ids,skipped_complement)
    filters = Filters(from_date=from_date, to_date=to_date)
    table = _get_stats_table(routes=routes,
                             filters=filters,
                             origin_id=origin_id,
                             destination_id=destination_id,
                             all_stops=True,
                             skipped_ids=skipped_ids)
    fields = ['week_day_local',
              'hour_local',
              'arrival_late_count',
              'num_trips',
              'stop_id'
              ]
    # we don't need all the fields
    table_list = []
    for t in table:
        entry = dict()
        for f in fields:
            entry[f] = t[f]
        table_list.append(entry)

    assert len(table_list) == len(table)
    result = {
        'table': table_list
    }
    return result


def get_path_info_full(origin_id, destination_id, from_date, to_date):
    routes = get_routes_from_to(origin_id, destination_id)
    filters = Filters(from_date=from_date, to_date=to_date)
    table = _get_stats_table(routes=routes, filters=filters,origin_id=origin_id, destination_id=destination_id)
    stats = _complete_table(table, [origin_id, destination_id])
    stats.sort(key=_get_info_sort_key)
    return stats


def get_routes_from_to(origin_id, destination_id, skipped_ids=None, skipped_complement=False):
    """
    :param origin_id: first stop
    :param destination_id: last stop
    :param skipped_ids: if given, will return routes that DOES NOT STOP in skipped_ids
    :return:
    """
    result = set()
    skipped_all = set()
    skipped_ids_set = set(skipped_ids) if skipped_ids else None
    for route in Route.objects.all():
        try:
            idx1 = route.stop_ids.index(origin_id)
            idx2 = route.stop_ids.index(destination_id)
        except ValueError:
            pass
        else:
            if idx1 < idx2:
                if route.trips.count() > 10:
                    result.add(route)
                    if skipped_ids and not (skipped_ids_set & set(route.stop_ids)):
                        skipped_all.add(route)
    if skipped_all:
        if skipped_complement:
            return result - skipped_all
        else:
            return skipped_all
    return result


def _get_info_sort_key(stat):
    info = stat['info']
    hours = info['hours'] if info['hours'] != 'all' else [1000, 1000]
    week_day = info['week_day'] if info['week_day'] != 'all' else 1000
    return week_day, hours


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


def _complete_table_for_all_stops(table):
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


def _get_select_postgres(*, route, filters, early_threshold, late_threshold):
    select_stmt = ('''
        SELECT  count(s.stop_id) as num_trips,
                s.gtfs_stop_id as gtfs_stop_id,
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
                   (' AND t.date >= %(start_date)s' if filters.from_date else '')
                   +
                   (' AND t.date <= %(to_date)s' if filters.to_date else '')
                   +
                   '''
                       GROUP BY s.gtfs_stop_id,week_day_local,hour_local
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


def _get_select_from_to_postgres(*, routes, filters, origin_id, destination_id, early_threshold, late_threshold, all_stops):
    route_ids = [r.id for r in routes]
    select_stmt = ('''
        SELECT  count(s.stop_id) as num_trips,
                s.gtfs_stop_id as gtfs_stop_id,
                t.x_week_day_local as week_day_local,
                extract(hour from timezone('Asia/Jerusalem', orig.exp_departure)) as hour_local,
                sum(case when s.delay_arrival <= %(early_threshold)s then 1 else 0 end) as arrival_early_count,
                sum(case when s.delay_arrival > %(early_threshold)s and s.delay_arrival < %(late_threshold)s then 1 else 0 end) as arrival_on_time_count,
                sum(case when s.delay_arrival >= %(late_threshold)s then 1 else 0 end) as arrival_late_count,

                sum(case when s.delay_departure <= %(early_threshold)s then 1 else 0 end) as departure_early_count,
                sum(case when s.delay_departure > %(early_threshold)s and s.delay_departure < %(late_threshold)s then 1 else 0 end) as departure_on_time_count,
                sum(case when s.delay_departure >= %(late_threshold)s then 1 else 0 end) as departure_late_count

        FROM
        data_route as r,
        data_trip as t,
        data_sample as s,
        data_sample as orig

        WHERE
        r.id =  ANY(%(route_ids)s)
        ''' +
        (' AND s.gtfs_stop_id = ANY(%(stop_ids)s) ' if not all_stops else '')
        + '''
        AND t.route_id = r.id
        AND t.valid
        AND s.trip_id = t.id
        AND orig.trip_id = t.id
        AND orig.gtfs_stop_id = %(origin_id)s
        ''' +
                   (' AND t.date >= %(start_date)s' if filters.from_date else '')
                   +
                   (' AND t.date <= %(to_date)s' if filters.to_date else '')
                   +
                   '''
                       GROUP BY s.gtfs_stop_id,week_day_local,hour_local
                   ''')
    select_kwargs = {
        'route_ids': route_ids,
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': [origin_id, destination_id],
        'start_date': filters.from_date,
        'to_date': filters.to_date,
        'origin_id': origin_id
    }
    return select_stmt, select_kwargs


@utils.benchit
def _get_stats_table(*, route=None,
                     routes=None,
                     origin_id=None,
                     destination_id=None,
                     filters=None,
                     all_stops=False,
                     skipped_ids=None):
    assert (route is None) ^ (routes is None), 'exactly one of route, routes must be None'
    early_threshold = -120
    late_threshold = 300
    if route:
        select_stmt, select_kwargs = _get_select_postgres(route=route, filters=filters,
                                                          early_threshold=early_threshold,
                                                          late_threshold=late_threshold)
    else:
        select_stmt, select_kwargs = _get_select_from_to_postgres(routes=routes,
                                                                  filters=filters,
                                                                  origin_id=origin_id,
                                                                  destination_id=destination_id,
                                                                  early_threshold=early_threshold,
                                                                  late_threshold=late_threshold,
                                                                  all_stops=all_stops)

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


def find_real_routes(from_date, to_date):
    logger.info("from_date = %s to_date = %s", from_date, to_date)
    trips = Trip.objects.filter(date__gte=from_date, date__lte=to_date)
    logger.info("# of trips = %d", trips.count())
    routes_with_counts = {r['route']: r['c'] for r in trips.values('route').annotate(c=Count('id'))}
    routes = list(Route.objects.filter(id__in=trips.values_list("route_id")))
    for r in routes:
        r.trips_count = routes_with_counts[r.id]

    logger.info("# of routes = %d", len(routes))
    to_remove = set()
    for r1 in routes:
        for r2 in routes:
            if r1.is_superset_of(r2) and r2 not in to_remove:
                to_remove.add(r2)
                r1.trips_count += r2.trips_count

    result = [r for r in routes if r not in to_remove]
    logger.info("There are %d real routes", len(result))
    result.sort(key=lambda r: r.trips_count, reverse=True)
    return result

