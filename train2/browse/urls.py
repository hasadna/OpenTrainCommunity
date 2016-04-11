from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    url(r'routes/?$', views.BrowseRoutes.as_view(), name='routes'),
    # url(r'routes/compare/?$',views.BrowseCompareRoutes.as_view(),name='compare_routes'),
    # url(r'routes/(?P<pk>\d+)/?$',views.BrowseRoute.as_view(),name='route'),
    # url(r'services/(?P<pk>\d+)/?$',views.BrowseService.as_view(),name='service'),
    # url(r'trips/(?P<pk>[\w\-]+)/?$',views.BrowseTrip.as_view(),name='trip'),
    # url(r'^raw-data', views.RawDateView.as_view(),name='raw-data')
]
