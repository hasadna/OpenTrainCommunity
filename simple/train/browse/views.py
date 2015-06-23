from data.models import Route,Service,Trip
from django.shortcuts import render, get_object_or_404

def _build_breadcrumbs(obj=None):
    if obj is None:
        return  [{
        'name': 'Routes',
        'link': '/browse/routes/'
    }]
    parent = obj.get_parent()
    return _build_breadcrumbs(parent) + [{
        'name': obj.get_short_name(),
        'link': '/browse/%ss/%s' % (obj.__class__.__name__.lower(),obj.id)
    }]

def browse_routes(req):
    routes = Route.objects.all()
    return render(req,'browse/browse_routes.html',{'routes':routes,
                                                   'breadcrumbs': _build_breadcrumbs()})

def browse_route(req,route_id):
    route = get_object_or_404(Route,pk=route_id)
    return render(req,'browse/browse_route.html',{'route':route,
                                                  'breadcrumbs': _build_breadcrumbs(route)})

def browse_service(req,service_id):
    service = get_object_or_404(Service,pk=service_id)
    return render(req,'browse/browse_service.html',{'service':service,
                                                    'breadcrumbs': _build_breadcrumbs(service)})

def browse_trip(req,trip_id):
    trip = get_object_or_404(Trip,pk=trip_id)
    samples = list(trip.sample_set.filter(is_real_stop=True).order_by('index'))
    return render(req,'browse/browse_trip.html',{'trip':trip,
                                                 'samples': samples,
                                                    'breadcrumbs': _build_breadcrumbs(trip)})

