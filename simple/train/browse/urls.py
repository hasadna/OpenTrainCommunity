from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
import views

urlpatterns = patterns('',
                       url(r'routes/?$',views.browse_routes),
                       url(r'routes/(?P<route_id>\d+)/?$',views.browse_route),
                       url(r'routes/(?P<route_id>\d+)/edit/?$',views.edit_route),
                       url(r'routes/(?P<route_id>\d+)/skip-stops/?$',views.skip_unskip_stops,{'skip':True}),
                       url(r'routes/(?P<route_id>\d+)/skip-stops/?$',views.skip_unskip_stops,{'skip':False}),
                       url(r'services/(?P<service_id>\d+)/?$',views.browse_service),
                       url(r'trips/(?P<trip_id>\w+)/?$',views.browse_trip),
                       #url(r'login/?$',views.login),
                       #url(r'logout/?$',views.logout),
                       url(r'^raw-data', views.show_raw_data))

