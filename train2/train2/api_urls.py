from django.conf.urls import url, include
from rest_framework import routers
import data.drf

router = routers.SimpleRouter()

router.register('stops', data.drf.StopViewSet)
router.register('stats', data.drf.StatViewSet, base_name="stats")
router.register('routes', data.drf.RoutesViewSet)
router.register('routes/(?P<route_id>\d+)/trips',
                data.drf.RouteTripsViewSet,
                base_name='route-trips')

# router.register('routes/(?P<route_id>\d+)/services',
#                 data.drf.RouteServicesViewSet,
#                 base_name='route-services')

# router.register('routes/(?P<route_id>\d+)/services/(?P<service_id>\d+)/trips',
#                 data.drf.RouteServicesViewSet,
#                 base_name='service-trips')

# router.register('routes/(?P<route_id>\d+)/services/(?P<service_id>\d+)/trips/(?P<trip_id>[^/.]+)/samples',
#                 data.drf.TripSamplesViewSet,
#                 base_name='trip-samples')
#


urlpatterns = [
    url(r'^', include(router.urls)),
]
