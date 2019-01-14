from django.conf.urls import url, include
from rest_framework import routers
import data.api
#import stories.api

router = routers.SimpleRouter()

router.register('stops', data.api.StopViewSet)
router.register('stats', data.api.StatViewSet, base_name="stats")
router.register('routes', data.api.RoutesViewSet)
router.register('trips', data.api.TripViewSet)
router.register('routes/(?P<route_id>\d+)/trips',
                data.api.RouteTripsViewSet,
                base_name='route-trips')

router.register('heat-map',
                data.api.HeatMapViewSet,
                base_name='heat-map')

router.register('general', data.api.GeneralViewSet, base_name='general')

router.register('highlights', data.api.HighlightsViewSet, base_name='highlights')

router.register('real-routes/(?P<year>\d{4})/(?P<month>\d{1,2})',
                data.api.RealRoutesViewSet, base_name='real-routes')

router.register('monthly', data.api.MonthlyViewSet, base_name='monthly')

#router.register('stories', stories.api.StoriesViewSet, base_name='stories')


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
