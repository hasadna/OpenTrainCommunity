from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name_len', 'english', 'hebrew_list_html', 'gtfs_stop_id', 'gtfs_code']
    search_fields = ['hebrew_list', 'english']

    def name_len(self, obj):
        return len(str(obj))

    name_len.short_description = 'name length'

    def hebrew_list_html(self, obj):
        return mark_safe('<br>'.join(escape(h) for h in obj.hebrew_list))

