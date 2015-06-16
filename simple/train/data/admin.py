from django.contrib import admin
from models import Route, Service, Trip, Sample
# Register your models here.

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('admin_unicode',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    pass

