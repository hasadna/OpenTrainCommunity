from django.conf.urls import url, include
from rest_framework import routers
import data.api

router = routers.SimpleRouter()

router.register('stops', data.api.StopViewSet)
router.register('stats', data.api.StatViewSet, base_name="stats")
router.register('routes', data.api.RoutesViewSet)
router.register('routes/(?P<route_id>\d+)/trips',
                data.api.RouteTripsViewSet,
                base_name='route-trips')

router.register('heat-map',
                data.api.HeatMapViewSet,
                base_name='heat-map')


# router.register('routes/(?P<route_id>\d+)/services',
#                 data.api.RouteServicesViewSet,
#                 base_name='route-services')

# router.register('routes/(?P<route_id>\d+)/services/(?P<service_id>\d+)/trips',
#                 data.api.RouteServicesViewSet,
#                 base_name='service-trips')

# router.register('routes/(?P<route_id>\d+)/services/(?P<service_id>\d+)/trips/(?P<trip_id>[^/.]+)/samples',
#                 data.api.TripSamplesViewSet,
#                 base_name='trip-samples')
#


urlpatterns = [
    url(r'^', include(router.urls)),
]
