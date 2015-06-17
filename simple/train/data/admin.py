from django.contrib import admin
import services
from models import Route, Service, Trip, Sample
from django.db.models import Count
# Register your models here.

admin.site.disable_action('delete_selected')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass
    #list_display = ('start_hour','end_hour')
    #def start_hour(self,obj):
    #    return obj.trip_set.all

class ServiceInline(admin.TabularInline):
    model = Service

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id','num_of_stops','first_stop','last_stop','num_of_services')
    inlines = [
        ServiceInline,
    ]

    def get_queryset(self, request):
        qs = super(RouteAdmin, self).queryset(request)
        return qs.annotate(service_count=Count('service'))

    def num_of_services(self,obj):
        return obj.service_count
    num_of_services.admin_order_field = 'service_count'

    def num_of_stops(self,obj):
        return len(obj.stop_ids)

    def first_stop(self,obj):
        return services.get_heb_stop_name(obj.stop_ids[0])

    def last_stop(self,obj):
        return services.get_heb_stop_name(obj.stop_ids[-1])

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    pass

