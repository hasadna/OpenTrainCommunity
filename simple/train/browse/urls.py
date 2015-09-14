from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
                       url(r'routes/?$',views.browse_routes),
                       url(r'routes/(?P<route_id>\d+)/?$',views.browse_route),
                       url(r'services/bad/?$',views.browse_bad_services,name='bad_services'),
                       url(r'services/(?P<service_id>\d+)/?$',views.browse_service),
                       url(r'trips/(?P<trip_id>\w+)/?$',views.browse_trip),
                       url(r'api/login/?$',views.login),
                       url(r'api/logout/?$',views.logout),
                       url(r'api/logged-in/?$',views.logged_in),
                       url(r'^raw-data', views.show_raw_data))

