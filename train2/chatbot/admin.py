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
    list_display = ['__str__', 'created_at', 'report_type']
    readonly_fields = [
        'session_nice', 'full_trip_nice', 'user_data_nice', 'att_list'
    ]
    exclude = ['session', 'full_trip', 'user_data']

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
        for att in obj.attachments:
            url = att['payload']['url']
            att_type = att['type']
            if att_type == 'image':
                result.append(f'''<img width="400">{url}</img><br/>''')
            else:
                result.append(f'<p><a href={url}>{att_type}</a></p>')
        return mark_safe(" ".join(result))

