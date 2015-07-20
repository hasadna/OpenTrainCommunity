from django.views.decorators.csrf import csrf_exempt
from data.models import Route,Service,Trip, Sample
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

def _build_breadcrumbs(obj=None):
    if obj is None:
        return  [{
        'name': _('Routes'),
        'link': '/browse/routes/'
    }]
    parent = obj.get_parent()
    if isinstance(obj,Sample):
        cur = {
            'name': '%s %s' % (_('File'),obj.data_file),
            'link': obj.get_text_link()
        }
    else:
        cur = {
            'name': obj.get_short_name(),
            'link': '/browse/%ss/%s' % (obj.__class__.__name__.lower(),obj.id)
        }
    return _build_breadcrumbs(parent) + [cur]

def _bc(obj,ctx):
    ctx['breadcrumbs'] = _build_breadcrumbs(obj)
    ctx['title'] = ctx['breadcrumbs'][-1]['name']
    return ctx

def browse_routes(req):
    routes = Route.objects.all()

    return render(req,'browse/browse_routes.html',_bc(None,{'routes':routes}))


def browse_route(req,route_id):
    route = get_object_or_404(Route,pk=route_id)
    return render(req,'browse/browse_route.html',_bc(route,{'route':route}))


def browse_service(req,service_id):
    service = get_object_or_404(Service,pk=service_id)
    return render(req,'browse/browse_service.html',_bc(service,{'service':service}))

def browse_trip(req,trip_id):
    trip = get_object_or_404(Trip,pk=trip_id)
    samples = list(trip.get_real_stop_samples())
    return render(req,'browse/browse_trip.html',_bc(trip,{'trip':trip,
                                                 'samples': samples}))

def show_raw_data(req):
    import codecs
    import os.path
    OFFSET = 20
    filename = req.GET['file']
    lineno = int(req.GET['line'])
    sample_id = int(req.GET['sample_id'])
    sample = get_object_or_404(Sample,pk=sample_id)
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
    ctx['prev'] =  sample.get_text_link(line=lineno - OFFSET * 2 - 1)
    ctx['next'] = sample.get_text_link(line=lineno + OFFSET * 2 - 1)
    return render(req, 'browse/browse_raw_data.html', _bc(sample,ctx))

def resp_json(d,status):
    import json
    return HttpResponse(content=json.dumps(d),status=status,content_type='application/json');

@csrf_exempt
def login(req):
    import django.contrib.auth
    username = req.POST['name']
    password = req.POST['password']
    user = django.contrib.auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            django.contrib.auth.login(req, user)
            error = None
            status = 201
        else:
            error = 'Disabled account'
            status = 401
    else:
        error = 'Invalid Login'
        status = 401
    d = user_to_auth_json(user)
    d['error'] = error
    return resp_json(d,status)


def user_to_auth_json(user):
    result = dict()
    result['logged_in'] = user and user.is_authenticated()
    if result['logged_in']:
        result['username'] = user.first_name or user.username
    else:
        result['username'] = ''
    return result

@csrf_exempt
def logout(req):
    import django.contrib.auth
    django.contrib.auth.logout(req)
    return resp_json(user_to_auth_json(req.user),status=201)

def logged_in(req):
    return resp_json(user_to_auth_json(req.user),status=200)
