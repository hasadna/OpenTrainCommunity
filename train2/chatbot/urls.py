from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views
urlpatterns = [
    url(r'^hook/?$', csrf_exempt(views.HookView.as_view()), name='hook'),
]

