from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import api_urls

admin.autodiscover()

urlpatterns = patterns('',
                       # url(r'^$', 'train.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       # url(r'^$', RedirectView.as_view(url='/ui/routes/', permanent=False)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'api/', include('data.urls', namespace='data')),
                       url(r'browse/', include('browse.urls', namespace='browse')),
                       url(r'^ui/routes/?$', 'data.views.route_explorer'),
                       url(r'^$', 'data.views.route_explorer'),
                       url(r'api/v1/', include(api_urls.router.urls)),
                       )
