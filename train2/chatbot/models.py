import datetime

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from .consts import ChatPlatform
from .att_utils import collect_attachments_from_payload


INITIAL_STEP = 'initial'


class ChatSessionQuerySet(models.QuerySet):
    def get_session(self, platform, sender_id):
        two_hours_ago = timezone.now() - datetime.timedelta(hours=2)
        try:
            return self.filter(
                platform=platform,
                user_id=sender_id,
                last_save_at__gte=two_hours_ago
            ).exclude(
                current_step__in=['terminate', 'goodbye']
            ).get()
        except ChatSession.DoesNotExist:
            return ChatSession.objects.create(
                platform=platform,
                user_id=sender_id
            )


class ChatSession(models.Model):
    user_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    current_step = models.CharField(max_length=50, default=INITIAL_STEP)
    payloads = JSONField(default=list)
    steps_data = JSONField(default=dict)
    last_save_at = models.DateTimeField(auto_now=True)
    platform = models.CharField(
        choices=ChatPlatform.choices, max_length=20, default=ChatPlatform.FACEBOOK)

    objects = ChatSessionQuerySet.as_manager()

    def __str__(self):
        return f'{self.user_id} started at @{self.created_at.replace(microsecond=0)}'

    @property
    def accept_payload_index(self):
        for idx, pl in enumerate(self.payloads):
            if pl['chat_step'] == 'accepted':
                return idx
        return -1

    class Meta:
        ordering = ('-created_at', '-id')


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_report_type_display()} report #{self.pk}'

    class Meta:
        ordering = ('-created_at', '-id')

    @property
    def platform(self):
        return self.session.platform

    @cached_property
    def generated_attachments(self):
        result = []
        for payload in self.session.payloads[self.session.accept_payload_index:]:
            result.extend(collect_attachments_from_payload(self.session, payload['payload']))
        return result
