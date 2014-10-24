from models import Sample, Trip
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
import itertools, dateutil.tz
from django.utils.timezone import make_naive, get_current_timezone

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


def get_relevant_routes(origin, destination, fromTime, toTime):
        routes = Trip.objects.raw('''SELECT id, stop_ids
        FROM public.data_trip
        WHERE valid
        AND ARRAY[%s::int,%s::int] <@ stop_ids
        ''', [origin, destination])

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

        return get_relevant_routes(origin, destination, fromTime, toTime)

    except Exception as e:
        print(e)


def get_delay_average(req):
    samples = get_relevant_routes_from_request(req)
    size = len(samples)
    average = 0
    for sample in samples:
        average += (sample[1].delay_arrival or 0) / size

    return HttpResponse(average)


#  from station to station, from time of day to time of day: delay average, % delays over threshold, delay/totalDuration
#  buckets of delays
# correlation between early lates in the routes
#