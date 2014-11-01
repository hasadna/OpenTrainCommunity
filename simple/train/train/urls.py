from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # url(r'^$', 'train.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^raw-data', 'data.views.show_raw_data'),
                       url(r'^api/routes/delays_over_duration', 'data.api.get_delay_over_total_duration'),
                       url(r'^api/routes/delays_buckets', 'data.api.get_delay_buckets'),
                       url(r'^api/routes/delays_over_threshold', 'data.api.get_delay_over_threshold'),
                       url(r'^api/routes/delays', 'data.api.get_delay'),
                       url(r'^api/routes/worst_station', 'data.api.get_worst_station_in_route'),
                       url(r'^api/routes', 'data.api.get_route'),
                       url(r'^api/stops/worst_direction','data.api.get_worst_direction'),
                       url(r'^api/stops','data.api.get_stops'),
                       url(r'^api/trips/(?P<trip_id>\w+)/','data.api.get_trip'),
                       url(r'^results/from-to', 'data.views.show_results_from_to')
)



