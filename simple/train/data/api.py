import datetime
from collections import namedtuple

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from . import errors
from .models import Route
from . import logic

Filters = namedtuple('Filters', ['from_date', 'to_date'])


def json_resp(obj, status=200):
    import json

    dumped_content = json.dumps(obj)
    return HttpResponse(content=dumped_content, content_type='application/json')


@cache_page(settings.CACHE_TTL)
def get_stops(req):
    from . import services

    stops = services.get_stops()
    stops.sort(key=lambda x: x['stop_name'])
    return json_resp(stops)


def get_trip(req, trip_id):
    from .models import Trip

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return json_resp({'error': '404',
                          'trip_id': trip_id},
                         status=404)
    return json_resp(trip.to_json())


@cache_page(settings.CACHE_TTL)
def get_all_routes(req):
    from django.db.models import Count, Min, Max
    min_count = req.GET.get('min_count',10)
    routes = list(Route.objects.all().order_by('id').annotate(
        trips_count=Count('trips'),
        min_date=Min('trips__start_date'),
        max_date=Max('trips__start_date')))

    routes = [r for r in routes if r.trips_count > min_count]

    result = []
    for r in routes:
        result.append({
            'id': r.id,
            'stop_ids': r.stop_ids,
            'count': r.trips_count,
            'min_date': logic.encode_date(r.min_date),
            'max_date': logic.encode_date(r.max_date)
        })
    return json_resp(result)


@cache_page(settings.CACHE_TTL)
def get_all_routes_by_date(req):
    from django.db.models import Count
    min_count = req.GET.get('min_count',10)
    from_date = logic.parse_date(req.GET['from_date'])
    to_date = logic.parse_date(req.GET['to_date'])

    routes = list(Route.objects
                  .filter(trips__start_date__gte=from_date, trips__start_date__lte=to_date)
                  .annotate(trips_count=Count('trips'))
                  .order_by('id'))

    routes = [r for r in routes if r.trips_count > min_count]

    result = [{'id': r.id, 'stop_ids': r.stop_ids, 'count': r.trips_count} for r in routes]
    return json_resp(result)


@cache_page(settings.CACHE_TTL)
def get_route_info_full(req):
    route_id = req.GET['route_id']
    from_date = logic.parse_date(req.GET.get('from_date'))
    to_date = logic.parse_date(req.GET.get('to_date'))
    if from_date and to_date and from_date > to_date:
        raise errors.InputError('from_date %s cannot be after to_date %s' % (from_date, to_date))
    return json_resp(logic.get_route_info_full(route_id, from_date, to_date))


#@cache_page(settings.CACHE_TTL)
def get_path_info_full(req):
    origin = int(req.GET['origin'])
    destination = int(req.GET['destination'])
    from_date = logic.parse_date(req.GET.get('from_date'))
    to_date = logic.parse_date(req.GET.get('to_date'))
    if from_date and to_date and from_date > to_date:
        raise errors.InputError('from_date %s cannot be after to_date %s' % (from_date, to_date))
    return json_resp(logic.get_path_info_full(origin, destination, from_date, to_date))
