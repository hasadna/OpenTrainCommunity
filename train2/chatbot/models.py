from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models


INITIAL_STEP = 'initial'


class ChatSession(models.Model):
    user_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    current_step = models.CharField(max_length=50, default=INITIAL_STEP)
    payloads = ArrayField(models.TextField(null=True), default=list)
    steps_data = JSONField(default=dict)
    last_save_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} started at @{self.created_at.replace(microsecond=0)}'


class ChatReport(models.Model):
    class ReportType:
        CANCEL = 'cancel'
        choices = [
            (CANCEL, CANCEL)
        ]
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    session = models.OneToOneField(ChatSession, related_name="report", on_delete=models.PROTECT)
    full_trip = JSONField()
    user_data = JSONField()

