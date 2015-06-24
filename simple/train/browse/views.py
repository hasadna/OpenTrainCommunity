from data.models import Route,Service,Trip
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings

def _build_breadcrumbs(obj=None):
    if obj is None:
        return  [{
        'obj': None,
        'name': _('Routes'),
        'link': '/browse/routes/'
    }]
    parent = obj.get_parent()
    return _build_breadcrumbs(parent) + [{
        'obj': obj,
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

def show_raw_data(req):
    import codecs
    import os.path
    OFFSET = 20
    filename = req.GET['file']
    lineno = int(req.GET['line'])
    from_lineno = max(0, lineno - OFFSET)
    to_lineno = (lineno + OFFSET)
    ctx = dict()
    cur_lineno = 1
    lines = []
    file_path = os.path.join(settings.TXT_FOLDER,filename)
    with codecs.open(file_path, encoding="windows-1255") as fh:
        for line in fh:
            if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                lines.append({'lineno': cur_lineno,
                              'line': line.strip().encode('utf-8', errors='ignore')})
            cur_lineno += 1
    ctx['lines'] = lines
    ctx['filename'] = filename
    ctx['lineno'] = lineno
    ctx['prev'] = '/raw-data?file=%s&line=%s' % (filename, lineno - OFFSET * 2 - 1)
    ctx['next'] = '/raw-data?file=%s&line=%s' % (filename, lineno + OFFSET * 2 + 1)
    return render(req, 'browse/browse_raw_data.html', ctx)
