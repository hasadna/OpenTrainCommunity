from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

from django.views.generic import RedirectView

urlpatterns = patterns('',
                       # url(r'^$', 'train.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^$', RedirectView.as_view(url='/ui/routes/', permanent=False)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^raw-data', 'data.views.show_raw_data'),
                       url(r'api/',include('data.urls')),
                       url(r'browse/routes/?$','data.views.browse_routes'),
                       url(r'browse/routes/(?P<route_id>\d+)/?$','data.views.browse_route'),
                       url(r'browse/services/(?P<service_id>\d+)/?$','data.views.browse_service'),
                       url(r'browse/trips/(?P<trip_id>\w+)/?$','data.views.browse_trip'),
                       url(r'^ui/routes/?$', 'data.views.route_explorer'),
)

