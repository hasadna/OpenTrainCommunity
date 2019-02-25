from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'link']

    def link(self, obj):
        return mark_safe(f'<a target="_blank" href={obj.next_url}>{obj.next_url}</a>')

