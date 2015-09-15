from django.shortcuts import render, get_object_or_404
from django.conf import settings

def show_results_from_to(req):
    return render(req, 'data/show_results.html', {'title': 'From To',
                                                  'app' : 'FromTo'})

def show_trip(req):
    return render(req,'data/show_results.html',{'title' : 'Show Trip',
                                             'app' : 'ShowTrip'})

def show_routes(req):
    return render(req,'data/show_results.html',{'title': 'Show Routes',
                                                'app': 'ShowRoutes'})
def route_explorer(req):
    return render(req, 'ui/RouteExplorer.html')


