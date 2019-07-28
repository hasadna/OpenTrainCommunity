import json

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from . import models


def nice_json(d):
    return mark_safe('<pre>{}</pre>'.format(json.dumps(d, indent=4, ensure_ascii=False).strip()))


@admin.register(models.ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'current_step']
    exclude = ['payloads', 'steps_data']
    readonly_fields = ['payloads_nice', 'steps_data_nice']

    def payloads_nice(self, obj):
        return mark_safe("\n".join('<pre>{}</pre>'.format(p) for p in obj.payloads))

    def steps_data_nice(self, obj):
        return nice_json(obj.steps_data)


def _mark_wrong_impl(modeladmin: admin.ModelAdmin, request, queryset, *, notify):
    if queryset.count() != 1:
        modeladmin.message_user(request, 'select exactly one', level=messages.ERROR)
        return
    for report in queryset:
        if not report.wrong_report:
            report.mark_as_wrong(notify=notify)


def mark_wrong_and_notify(modeladmin: admin.ModelAdmin, request, queryset):
    _mark_wrong_impl(modeladmin, request, queryset, notify=True)


mark_wrong_and_notify.short_description = "Mark selected report as wrong and notify"


def mark_wrong(modeladmin: admin.ModelAdmin, request, queryset):
    _mark_wrong_impl(modeladmin, request, queryset, notify=False)


mark_wrong.short_description = "Mark selected report as wrong (no notify)"


@admin.register(models.ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'real_report', 'wrong_report', 'report_type', 'attachments_count']
    readonly_fields = [
        'session_nice', 'full_trip_nice', 'user_data_nice', 'att_list'
    ]
    exclude = ['session', 'full_trip', 'user_data', 'attachments']

    actions = [mark_wrong_and_notify, mark_wrong]

    def attachments_count(self, obj):
        return len(obj.generated_attachments)

    def session_nice(self, obj):
        return mark_safe('<a href=/admin/chatbot/chatsession/{}/change/>{}</a>'.format(
            obj.session_id,
            obj.session
        ))

    def full_trip_nice(self, obj):
        return nice_json(obj.full_trip)

    def user_data_nice(self, obj):
        return nice_json(obj.user_data)

    def att_list(self, obj):
        result = []
        for att in obj.generated_attachments:
            url = att.url
            att_type = att.type
            if att_type == 'image':
                result.append(f'''<img style="margin: 5px" width="400" src="{url}"><br/>''')
            if att_type == 'video':
                result.append(f'<video src="{url}" controls><a target="_blank" href={url}>link to {att_type}</a></video>')
            result.append(f'<p><a target="_blank" href={url}>link to {att_type}</a></p>')
        return mark_safe(" ".join(result))

