from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       #url(r'^routes/?$', 'data.api.get_route'),
                       url(r'^all-routes/?$', 'data.api.get_all_routes'),
                       url(r'^all-routes-by-date/?$', 'data.api.get_all_routes_by_date'),
                       #url(r'^path-info/?$', 'data.api.get_path_info'),
                       #url(r'^path-info-full/?$', 'data.api.get_path_info_full'),
                       url(r'^route-info-full/?$', 'data.api.get_route_info_full'),
                       url(r'^path-info-full/?$', 'data.api.get_path_info_full'),
                       url(r'^stops/?$', 'data.api.get_stops'))
