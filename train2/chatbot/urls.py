from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^hello-world/$', views.HelloWorldView.as_view(), name='hello-world'),
]
