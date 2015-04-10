from models import Sample, Trip, Route
from django.http import HttpResponse, Http404
from django.db.models import Q
import cache_utils
import django.db


def json_resp(obj, status=200):
    import json

    dumped_content = json.dumps(obj)
    return HttpResponse(content=dumped_content, content_type='application/json')


@cache_utils.cacheit
def get_stops(req):
    import services

    stops = services.get_stops()
    stops.sort(key=lambda x: x['stop_name'])
    return json_resp(stops)


def get_trip(req, trip_id):
    from models import Trip

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return json_resp({'error': '404',
                          'trip_id': trip_id},
                         status=404)
    return json_resp(trip.to_json());


@cache_utils.cacheit
def get_all_routes(req):
    from django.db.models import Count

    routes = list(Route.objects.all().order_by('id').annotate(trips_count=Count('trip')))
    result = []
    for r in routes:
        # stop_ids = r.stop_ids
        # stops = [{'stop_id': stop_id} for stop_id in stop_ids]
        result.append(
            {'stop_ids': r.stop_ids,
             'count': r.trips_count}
        )
    return json_resp(result)


def contains_stops(route, stop_ids):
    route_stop_ids = route.stop_ids
    try:
        first_index = route_stop_ids.index(stop_ids[0])
    except ValueError:
        return False
    return route_stop_ids[first_index:len(stop_ids) + first_index] == stop_ids


def find_all_routes_with_stops(stop_ids):
    routes = Route.objects.all()
    result = [r for r in routes if contains_stops(r, stop_ids)]
    return result


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


@cache_utils.cacheit
def get_path_info(req):
    stop_ids = [int(s) for s in req.GET['stop_ids'].split(',')]
    routes = find_all_routes_with_stops(stop_ids)
    trips = []
    for r in routes:
        trips.extend(list(r.trip_set.filter(valid=True)))
    stat = _get_path_info_partial(stop_ids,
                                  routes=routes,
                                  all_trips=trips,
                                  week_day='all',
                                  hours='all')

    return json_resp(stat['stops'])


def _get_info_sort_key(info):
    hours = info['hours'] if info['hours'] != 'all' else (1000,1000)
    week_day = info['week_day'] if info['week_day'] != 'all' else 1000
    return week_day,hours

@cache_utils.cacheit
def get_path_info_full(req):
    stop_ids = [int(s) for s in req.GET['stop_ids'].split(',')]
    # find all routes whose contains these stop ids
    routes = find_all_routes_with_stops(stop_ids)
    trips = []
    for r in routes:
        trips.extend(list(r.trip_set.filter(valid=True)))

    stats = []
    for hours in HOURS + ['all']:
        kwargs = dict(stop_ids=stop_ids,
                      routes=routes,
                      all_trips=trips,
                      #week_day=week_day,
                      hours=hours)
        cur_stats = _get_path_info_per_weekdays(**kwargs)
        stats.extend(cur_stats)
    stats.sort(key=lambda x: _get_info_sort_key(x['info']))
    return json_resp(stats)


def _get_path_info_per_weekdays(stop_ids, routes, all_trips, hours):
    result = []
    early_threshold = -120
    late_threshold = 300
    trips = all_trips[:]
    trip_ids = [t.id for t in trips]
    first_stop_id = stop_ids[0]
    if hours != 'all':
        # find the trips that the first stop_id ***exp*** departure in between the hours range ***
        qs = Sample.objects.filter(trip_id__in=trip_ids,
                                   stop_id=first_stop_id)
        hour_or_query = None
        for hour in range(*hours):
            new_query = Q(exp_departure__hour=(hour % 24))
            if hour_or_query is None:
                hour_or_query = new_query
            else:
                hour_or_query = hour_or_query | new_query
        qs = qs.filter(hour_or_query)
        trip_ids = list(qs.values_list('trip_id', flat=True))
        trips = [t for t in trips if t.id in trip_ids]
    select_stmt = '''
        SELECT  s.stop_id as stop_id,
                avg(case when delay_arrival <= %(early_threshold)s then 1.0 else 0.0 end)::float as arrival_early_pct,
                avg(case when delay_arrival > %(early_threshold)s and delay_arrival < %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_on_time_pct,
                avg(case when delay_arrival >= %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_late_pct,

                avg(case when delay_departure <= %(early_threshold)s then 1.0 else 0.0 end)::float as departure_early_pct,
                avg(case when delay_departure > %(early_threshold)s and delay_departure < %(late_threshold)s then 1.0 else 0.0 end)::float as departure_on_time_pct,
                avg(case when delay_departure >= %(late_threshold)s then 1.0 else 0.0 end)::float as departure_late_pct

        FROM    data_sample as s
        WHERE   s.stop_id = ANY (ARRAY[%(stop_ids)s])
        AND     s.valid
        AND     s.trip_id = ANY (ARRAY[%(trip_ids)s])
        GROUP BY s.stop_id
    '''
    select_kwargs = {
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': stop_ids,
        'trip_ids': trip_ids,
    }
    info = {
        'num_trips': len(trips),
        'week_day': 'all',
        'hours': hours,
    }

    cursor = django.db.connection.cursor()
    cursor.execute(select_stmt,select_kwargs)
    cols = [
        'stop_id',
        'arrival_early_pct', 'arrival_on_time_pct', 'arrival_late_pct',
        'departure_early_pct', 'departure_on_time_pct', 'departure_late_pct'
    ]
    stats_map = {}
    for row in cursor:
        stat = dict(zip(cols, row))
        stats_map[stat['stop_id']] = stat

    result.append({
        'info': info,
        'stops': list(stats_map.get(stop_id, {}) for stop_id in stop_ids)
    })

    trips = all_trips[:]
    trip_ids = [t.id for t in trips]
    if hours != 'all':
        # find the trips that the first stop_id ***exp*** departure in between the hours range ***
        qs = Sample.objects.filter(trip_id__in=trip_ids,
                                   stop_id=first_stop_id)
        hour_or_query = None
        for hour in range(*hours):
            new_query = Q(exp_departure__hour=(hour % 24))
            if hour_or_query is None:
                hour_or_query = new_query
            else:
                hour_or_query = hour_or_query | new_query
        qs = qs.filter(hour_or_query)
        trip_ids = list(qs.values_list('trip_id', flat=True))
        trips = [t for t in trips if t.id in trip_ids]
    select_stmt = '''
        SELECT  s.stop_id as stop_id,
                extract(dow from t.start_date) as week_day_pg,
                avg(case when delay_arrival <= %(early_threshold)s then 1.0 else 0.0 end)::float as arrival_early_pct,
                avg(case when delay_arrival > %(early_threshold)s and delay_arrival < %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_on_time_pct,
                avg(case when delay_arrival >= %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_late_pct,

                avg(case when delay_departure <= %(early_threshold)s then 1.0 else 0.0 end)::float as departure_early_pct,
                avg(case when delay_departure > %(early_threshold)s and delay_departure < %(late_threshold)s then 1.0 else 0.0 end)::float as departure_on_time_pct,
                avg(case when delay_departure >= %(late_threshold)s then 1.0 else 0.0 end)::float as departure_late_pct,
                count(s.stop_id) as num_trips

        FROM    data_sample as s JOIN data_trip as t
        ON s.trip_id = t.id
        WHERE   s.stop_id = ANY (ARRAY[%(stop_ids)s])
        AND     s.valid
        AND     s.trip_id = ANY (ARRAY[%(trip_ids)s])
        GROUP BY s.stop_id,week_day_pg
    '''
    select_kwargs = {
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': stop_ids,
        'trip_ids': trip_ids,
    }

    cursor = django.db.connection.cursor()
    cursor.execute(select_stmt,select_kwargs)

    cols = [
        'stop_id',
        'week_day_pg',
        'arrival_early_pct', 'arrival_on_time_pct', 'arrival_late_pct',
        'departure_early_pct', 'departure_on_time_pct', 'departure_late_pct',
        'num_trips'
    ]

    stats_map = {}
    num_trips = None
    from collections import defaultdict
    all_stats = defaultdict(dict)
    for row in cursor:
        stat = dict(zip(cols, row))
        all_stats[int(stat['week_day_pg']) + 1][stat['stop_id']] = stat

    for week_day in WEEK_DAYS:
        stats_map = all_stats[week_day]
        num_trips = None
        for k,v in stats_map.iteritems():
            old_num_trips = num_trips
            num_trips = v['num_trips']
            if old_num_trips is not None:
                assert num_trips == old_num_trips,'Inconsistent num trips'
        info = {
            'num_trips': num_trips or 0,
            'week_day': week_day,
            'hours': hours
        }
        entry = {
            'info': info,
            'stops': list(stats_map.get(stop_id, {}) for stop_id in stop_ids)
        }
        for stop in entry['stops']:
            stop.pop('week_day_pg',0)
            stop.pop('num_trips',0)
        result.append(entry)

    return result




def _get_path_info_partial(stop_ids, routes, all_trips, week_day, hours):
    assert 1 <= week_day <= 7 or week_day == 'all', 'Illegal week_day %s' % (week_day,)
    early_threshold = -120
    late_threshold = 300
    all_trip_ids = [trip.id for trip in all_trips]
    if week_day != 'all':
        trips = Trip.objects.filter(id__in=all_trip_ids, start_date__week_day=week_day)
    else:
        trips = all_trips
    trip_ids = [t.id for t in trips]
    first_stop_id = stop_ids[0]
    if hours != 'all':
        # find the trips that the first stop_id ***exp*** departure in between the hours range ***
        qs = Sample.objects.filter(trip_id__in=trip_ids,
                                   stop_id=first_stop_id)
        hour_or_query = None
        for hour in range(*hours):
            new_query = Q(exp_departure__hour=(hour % 24))
            if hour_or_query is None:
                hour_or_query = new_query
            else:
                hour_or_query = hour_or_query | new_query
        qs = qs.filter(hour_or_query)
        trip_ids = list(qs.values_list('trip_id', flat=True))
        trips = [t for t in trips if t.id in trip_ids]
    select_stmt = '''
        SELECT  s.stop_id as stop_id,
                avg(case when delay_arrival <= %(early_threshold)s then 1.0 else 0.0 end)::float as arrival_early_pct,
                avg(case when delay_arrival > %(early_threshold)s and delay_arrival < %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_on_time_pct,
                avg(case when delay_arrival >= %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_late_pct,

                avg(case when delay_departure <= %(early_threshold)s then 1.0 else 0.0 end)::float as departure_early_pct,
                avg(case when delay_departure > %(early_threshold)s and delay_departure < %(late_threshold)s then 1.0 else 0.0 end)::float as departure_on_time_pct,
                avg(case when delay_departure >= %(late_threshold)s then 1.0 else 0.0 end)::float as departure_late_pct

        FROM    data_sample as s
        WHERE   s.stop_id = ANY (ARRAY[%(stop_ids)s])
        AND     s.valid
        AND     s.trip_id = ANY (ARRAY[%(trip_ids)s])
        GROUP BY s.stop_id
    '''
    select_kwargs = {
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': stop_ids,
        'trip_ids': trip_ids,
    }
    info = {
        'num_trips': len(trips),
        'week_day': week_day,
        'hours': hours,
    }

    cursor = django.db.connection.cursor()
    cursor.execute(select_stmt,select_kwargs)
    cols = [
        'stop_id',
        'arrival_early_pct', 'arrival_on_time_pct', 'arrival_late_pct',
        'departure_early_pct', 'departure_on_time_pct', 'departure_late_pct'
    ]
    stats_map = {}
    for row in cursor:
        stat = dict(zip(cols, row))
        stats_map[stat['stop_id']] = stat

    return {
        'info': info,
        'stops': list(stats_map.get(stop_id, {}) for stop_id in stop_ids)
    }

