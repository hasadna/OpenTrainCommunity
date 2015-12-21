from django.conf.urls import url, include
from rest_framework import routers
import data.drf

router = routers.SimpleRouter()
router.register('routes',data.drf.RoutesViewSet)
router.register('routes/(?P<route_id>\d+)/trips', data.drf.TripViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

]

