from models import Sample, Trip
from django.http import HttpResponse,Http404
from django.core import serializers
from django.db.models import Q
import itertools, datetime, json
from django.utils.timezone import make_naive, get_current_timezone
from collections import Counter
from django.conf import settings


def json_resp(obj,status=200):
    import json
    return HttpResponse(content=json.dumps(obj),content_type='application/json')


def show_sample(req):
    try:
        sample = Sample.objects.filter(stop_id=req.GET.get('stop_id'), valid=True, is_real_stop=True)

        response = HttpResponse(serializers.serialize('json', sample))
        print(response)
        return response
    except Exception as e:
        print(e)


def get_departure_hour(sample):
    return make_naive(sample.exp_departure, get_current_timezone()).hour


def get_stops(req):
    import services
    stops = services.get_stops()
    stops.sort(key=lambda x : x['stop_name'])
    return json_resp(stops)


def get_relevant_routes(origin, destination, fromTime, toTime, days):
        routes = Trip.objects.raw('''SELECT id, stop_ids
        FROM public.data_trip
        WHERE valid
        AND ARRAY[%s::int,%s::int] <@ stop_ids
        AND EXTRACT(dow FROM start_date)::int = ANY(%s)
        ''', [origin, destination, days])

        trips = [route.id for route in routes if route.stop_ids.index(int(origin)) < route.stop_ids.index(int(destination))]

        samples = list(Sample.objects.filter(Q(stop_id=destination) | Q(stop_id=origin)).filter(trip_name__in=trips).order_by('trip_name'))

        filteredSamples = []
        for firstSample, secondSample in itertools.izip(samples[::2], samples[1::2]):
            # if(firstSample.id == 14):
            #     print(firstSample.id, make_naive(firstSample.exp_departure, get_current_timezone()))
            if (firstSample.stop_id == origin and fromTime <= get_departure_hour(firstSample) <= toTime) or \
                    (secondSample.stop_id == origin and fromTime <= get_departure_hour(secondSample) <= toTime):
                filteredSamples.append((firstSample, secondSample) if firstSample.stop_id == origin else (secondSample, firstSample))

        return filteredSamples


def get_relevant_routes_from_request(req):
    try:
        origin = int(req.GET.get('from'))
        destination = int(req.GET.get('to'))
        fromTime = int(req.GET.get('from_time') or 0)
        toTime = int(req.GET.get('to_time') or 23)
        days = req.GET.get('days')
        days = (days and map(int, days.split(','))) or list(range(0,6))

        return get_relevant_routes(origin, destination, fromTime, toTime, days)

    except Exception as e:
        print(e)


def get_delay_from_data(samples):
    size = len(samples)

    if size == 0:
        return {}

    delays = [sample[1].delay_arrival or 0 for sample in samples]
    average = sum(delays) / size
    minimum = min(delays)
    maximum = max(delays)

    minTrips = [sample[1].trip_name for sample in samples if sample[1].delay_arrival == minimum]
    maxTrips = [sample[1].trip_name for sample in samples if sample[1].delay_arrival == maximum]

    return {'min': {
        'duration': minimum,
        'trips': minTrips
    }, 'max': {
        'duration': maximum,
        'trips': maxTrips
    },
        'average': average
    }


def get_delay(req):
    samples = get_relevant_routes_from_request(req)
    return HttpResponse(json.dumps(get_delay_from_data(samples)))


def get_delay_over_total_duration_from_data(samples):
    delay = 0
    duration = datetime.timedelta()
    for sample in samples:
        if len(sample) != 2:
            continue

        delay += (sample[1].delay_arr0ival or 0)
        duration += sample[1].exp_arrival - sample[0].exp_departure
    res = delay / duration.total_seconds()
    return res


def get_delay_over_total_duration(req):
    samples = get_relevant_routes_from_request(req)
    return HttpResponse(get_delay_over_total_duration_from_data(samples))

def get_trip(req,trip_id):
    from models import Trip
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return json_resp({'error' : '404',
                          'trip_id' : trip_id},
                         status=404)
    return json_resp(trip.to_json());

def get_delay_buckets(req):
    if req.GET.get('from'):  # TODO: check all routes
        samples = get_relevant_routes_from_request(req)
        delays = [sample[1].delay_arrival or 0 for sample in samples]
        res = {}
        for key, value in dict(Counter([delay//300 for delay in delays])).iteritems():
            res[key*5] = value
        return HttpResponse(res)

def get_delay_over_threshold_from_data(samples, threshold):
    delaysOverThreshold = len([sample[1].delay_arrival for sample in samples if sample[1].delay_arrival >= threshold])
    res = {'nominal': delaysOverThreshold, 'proportional': float(delaysOverThreshold) / len(samples)}
    return res

def get_delay_over_threshold(req):
    samples = get_relevant_routes_from_request(req)
    threshold = int(req.GET.get('threshold'))
    return HttpResponse(json.dumps(get_delay_over_threshold_from_data(samples, threshold)))


def get_worst_station_from_data(samples):
    trips = [sample[0].trip_name for sample in samples]
    allStops = Sample.objects.filter(trip_name__in=trips).filter(delay_arrival__gt=600).order_by('trip_name')
    worstSamples = []
    for trip, samples in itertools.groupby(allStops, lambda sample: sample.trip_name):
        worstSamples.append(max(samples, key=lambda sample: sample.delay_arrival))
    return dict(Counter([sample.stop_id for sample in worstSamples]))

def get_worst_station_in_route_helper(req):
    samples = get_relevant_routes_from_request(req)
    return get_worst_station_from_data(samples)


def get_worst_station_in_route(req):
    return HttpResponse(json.dumps(get_worst_station_in_route_helper(req)))


def get_dates_range(samples):
    dates = [sample[0].actual_departure for sample in samples if sample[0].actual_departure != None]
    return {
        'first': min(dates).isoformat(),
        'last': max(dates).isoformat()
    }


def get_route(req):
    samples = get_relevant_routes_from_request(req)
    if len(samples) == 0:
        return json_resp({'total': 0})

    res = get_delay_from_data(samples)
    res['delay_2'] = get_delay_over_threshold_from_data(samples, 2*60)
    res['delay_5'] = get_delay_over_threshold_from_data(samples, 5*60)
    res['total'] = len(samples)
    res['dates'] = get_dates_range(samples)
    return json_resp(res)

def get_routes_from_db():
    from django.db import connection
    with connection.cursor() as c:
        c.execute("select stop_ids,count(*) as num_stops from data_trip where valid group by stop_ids order by num_stops DESC")
        routes = c.fetchall()
        return routes

def get_all_routes(req):
    import services
    t1 = time.time()
    routes = get_routes_from_db()
    if settings.DEBUG:
        print django.db.connection.queries[-1]
        t2 = time.time()
        print 't2 - t1 = %s' % (t2-t1)
    result = []
    for r in routes:
        stop_ids = r[0]
        stops = [services.get_stop(sid) for sid in stop_ids]
        result.append(
            {'stops' : stops,
             'count' : r[1]}
        )
    return json_resp(result)
import time

import django.db

def fill_stop_info(stop, stop_ids):
    t3 = time.time()
    samples = list(Sample.objects.filter(stop_ids=stop_ids,
                                         stop_id=stop['gtfs_stop_id'],
                                         valid=True).values('delay_arrival','delay_departure'))
    #print django.db.connection.queries[-1]
    #print len(samples)
    t4 = time.time()
    print 't4 - t3 = %.3f' % (t4-t3)
    samples_len = float(len(samples))
    stop['avg_delay_arrival'] = sum(x['delay_arrival'] or 0.0 for x in samples)/samples_len
    stop['avg_delay_departure'] = sum(x['delay_departure'] or 0.0 for x in samples)/samples_len
    stop['delay_arrival_gte2'] = sum(1 if x['delay_arrival'] >= 120 else 0 for x in samples)/samples_len
    stop['delay_arrival_gte5'] = sum(1 if x['delay_arrival'] >= 300 else 0 for x in samples)/samples_len
    t5 = time.time()
    print 't5 - t4 = %.3f' % (t5-t4)

import threading

def get_route_info(req):
    import services
    t1 = time.time()
    stop_ids = [int(s) for s in req.GET['stop_ids'].split(',')]
    trips_len = Trip.objects.filter(stop_ids=stop_ids).count()
    stops = [services.get_stop(sid) for sid in stop_ids]
    t2 = time.time()
    print 't2 - t1 = %.3f' % (t2-t1)
    use_threads = False #True
    if use_threads:
        threads = []
        for stop in stops:
            t = threading.Thread(target=fill_stop_info,args=(stop,stop_ids))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    else:
        for stop in stops:
            fill_stop_info(stop, stop_ids)

    result = {
        'count' : trips_len,
        'stops' : stops,
    }
    t3 = time.time()
    return json_resp(result)

def get_path_info(req):
    import services

    stop_ids = [int(s) for s in req.GET['stop_ids'].split(',')]
    stop_ids_str = ','.join(str(stop_id) for stop_id in stop_ids)

    cursor =  django.db.connection.cursor();
    cursor.execute('''
        SELECT  s.stop_id as stop_id,
                avg(coalesce(delay_arrival, 0.0)) as arrival_avg_delay,
                avg(case when delay_arrival < 0 then 1.0 else 0.0 end)::float as arrival_early_pct,
                avg(case when delay_arrival >= 0 and delay_arrival < 120 then 1.0 else 0.0 end)::float as arrival_on_time_pct,
                avg(case when delay_arrival >= 120 and delay_arrival < 300 then 1.0 else 0.0 end)::float as arrival_short_delay_pct,
                avg(case when delay_arrival >= 300 then 1.0 else 0.0 end)::float as arrival_long_delay_pct,

                avg(coalesce(delay_departure, 0.0)) as departure_avg_delay,
                avg(case when delay_departure < 0 then 1.0 else 0.0 end)::float as departure_early_pct,
                avg(case when delay_departure >= 0 and delay_departure < 120 then 1.0 else 0.0 end)::float as departure_on_time_pct,
                avg(case when delay_departure >= 120 and delay_departure < 300 then 1.0 else 0.0 end)::float as departure_short_delay_pct,
                avg(case when delay_departure >= 300 then 1.0 else 0.0 end)::float as departure_long_delay_pct

        FROM    data_sample as s INNER JOIN data_trip as t ON s.trip_id = t.id
        WHERE   s.stop_id = ANY (%(stop_ids)s)
        AND     s.valid
        AND     t.stop_ids @> %(stop_ids)s
        AND     position(%(stop_ids_str)s in array_to_string(t.stop_ids, ',')) > 0
        GROUP BY s.stop_id
    ''', { 'stop_ids': stop_ids, 'stop_ids_str': stop_ids_str })

    cols = [
        'stop_id',
        'arrival_avg_delay', 'arrival_early_pct', 'arrival_on_time_pct', 'arrival_short_delay_pct', 'arrival_long_delay_pct',
        'departure_avg_delay', 'departure_early_pct', 'departure_on_time_pct', 'departure_short_delay_pct', 'departure_long_delay_pct'
    ]

    stats_map = {}
    for row in cursor:
        stat = dict(zip(cols, row))
        stats_map[stat['stop_id']] = stat

    return json_resp(list(stats_map[stop_id] for stop_id in stop_ids))
