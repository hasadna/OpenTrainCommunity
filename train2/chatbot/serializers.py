from rest_framework import serializers

from . import models


class ChatReportSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, obj):
        return [{
            'type': a.type,
            'url': a.url
        } for a in obj.generated_attachments]

    class Meta:
        model = models.ChatReport
        fields = [
            'id',
            'wrong_report',
            'created_at',
            'reported_from',
            'reported_to',
            'trip',
            'platform',
            'attachments',
            'trip_id',
            'trip_id_reports',
        ]
