from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

from django.views.generic import RedirectView

urlpatterns = patterns('',
                       # url(r'^$', 'train.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^$', RedirectView.as_view(url='/ui/routes/', permanent=False)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^raw-data', 'data.views.show_raw_data'),
                       url(r'api/',include('data.urls')),
                       url(r'^ui/routes/?$', 'data.views.route_explorer'),
)

