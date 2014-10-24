from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'train.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^raw-data','data.views.show_raw_data'),
    # url(r'^api/sample.*', 'data.api.show_sample'),
    url(r'^api/routes/delays', 'data.api.get_delay_average')
)


