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

        delay += (sample[1].delay_arrival or 0)
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


def get_worst_direction(req):
    try:
     stop = int(req.GET.get('stop'))
     samples = Sample.objects.filter(stop_id=stop, is_real_stop=True, valid=True)
     if len(samples) == 0:
         return json_resp({'total': 0})

     trips = Trip.objects.filter(id__in=[sample.trip_name for sample in samples])
     toNorth = [trip for trip in trips if trip.is_to_north()]
     toSouth = [trip for trip in trips if not trip.is_to_north()]

     northDelays = sum([sample.delay_arrival for sample in samples if sample.trip_name in toNorth]) / len(toNorth)
     southDelays = sum([sample.delay_arrival for sample in samples if sample.trip_name in toSouth]) / len(toSouth)

     res = {
         'worst': 'North' if northDelays > southDelays else 'South',
         'percentage': (abs(northDelays-southDelays)/max(northDelays,southDelays,1))
     }

     return json_resp(res)
    except Exception as e:
        print(e)


