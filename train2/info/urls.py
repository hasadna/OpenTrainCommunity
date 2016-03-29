from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^routes/$',views.RoutesView.as_view(),name='routes')
        ]
