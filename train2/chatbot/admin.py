import json

from django.contrib import admin
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


@admin.register(models.ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'report_type', 'attachments_count']
    readonly_fields = [
        'session_nice', 'full_trip_nice', 'user_data_nice', 'att_list'
    ]
    exclude = ['session', 'full_trip', 'user_data', 'attachments']

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

