from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^hook/$', views.HookView.as_view(), name='hook'),
]
