from django.contrib import admin
from . import models


@admin.register(models.ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'current_step']


@admin.register(models.ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'report_type']
    readonly_fields = [
        'session'
    ]

