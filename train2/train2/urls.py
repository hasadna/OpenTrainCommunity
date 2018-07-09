"""train2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

import ui.views
import ui2.views
from . import api_urls
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', ui.views.RouteExplorer.as_view()),
    url(r'^ui2/$', ui2.views.AppView.as_view()),
    url(r'api/v1/', include(api_urls.router.urls)),
    url(r'^info/',include('info.urls',namespace="info")),
    url(r'^api/docs/', schema_view),
]

