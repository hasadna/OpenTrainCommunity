from django.contrib import admin
from .models import Service, Trip, Route, Sample

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	list_display = ('route', 'local_time_str')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
	list_display = ('train_num', 'start_date', 'valid', \
		'route', 'trip_name', 'start_date', \
		'service',  'x_week_day_local', 'x_hour_local')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
	list_display = ('id', 'stop_ids', )

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
	list_display = ('stop_id', 'stop_name', 'is_skipped', \
		'valid', 'is_first', 'is_last', 'actual_arrival', \
		'exp_arrival', 'delay_arrival', 'actual_departure', \
		'exp_departure', 'delay_departure', 'data_file', \
    	'data_file_line', 'trip', 'version', 'is_planned', \
    	'is_stopped')




