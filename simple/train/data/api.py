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


@cache_utils.cacheit
def get_path_info_full(req):
    stop_ids = [int(s) for s in req.GET['stop_ids'].split(',')]
    # find all routes whose contains these stop ids
    routes = find_all_routes_with_stops(stop_ids)
    trips = []
    for r in routes:
        trips.extend(list(r.trip_set.filter(valid=True)))

    hours_len = len(HOURS) + 1
    days_len = len(WEEK_DAYS) + 1
    stats = [None] * hours_len * days_len
    for idx1, week_day in enumerate(WEEK_DAYS + ['all']):
        for idx2, hours in enumerate(HOURS + ['all']):
            index = idx1 * hours_len + idx2
            args = (stats, index)
            kwargs = dict(stop_ids=stop_ids,
                          routes=routes,
                          all_trips=trips,
                          week_day=week_day,
                          hours=hours)
            _start_get_path_info_partial(*args, **kwargs)
    return json_resp(stats)


def _start_get_path_info_partial(stats, index, **kwargs):
    stat = _get_path_info_partial(**kwargs)
    stats[index] = stat


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
    cursor = django.db.connection.cursor()
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

    cursor.execute('''
        SELECT  s.stop_id as stop_id,
                avg(case when delay_arrival <= %(early_threshold)s then 1.0 else 0.0 end)::float as arrival_early_pct,
                avg(case when delay_arrival > %(early_threshold)s and delay_arrival < %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_on_time_pct,
                avg(case when delay_arrival >= %(late_threshold)s then 1.0 else 0.0 end)::float as arrival_late_pct,

                avg(case when delay_departure <= %(early_threshold)s then 1.0 else 0.0 end)::float as departure_early_pct,
                avg(case when delay_departure > %(early_threshold)s and delay_departure < %(late_threshold)s then 1.0 else 0.0 end)::float as departure_on_time_pct,
                avg(case when delay_departure >= %(late_threshold)s then 1.0 else 0.0 end)::float as departure_late_pct

        FROM    data_sample as s
        WHERE   s.stop_id = ANY (%(stop_ids)s)
        AND     s.valid
        AND     s.trip_id = ANY (%(trip_ids)s)
        GROUP BY s.stop_id
    ''', {
        'early_threshold': early_threshold,
        'late_threshold': late_threshold,
        'stop_ids': stop_ids,
        'trip_ids': trip_ids
    })

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
        'info': {
            'num_trips': len(trips),
            'week_day': week_day,
            'hours': hours,
        },
        'stops': list(stats_map.get(stop_id, {}) for stop_id in stop_ids)
    }


