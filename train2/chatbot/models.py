from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models


class STEPS:
    WELCOME = 'welcome'
    IS_TRAIN_AROUND_NOW = 'is_train_around_now'
    USER_LOCATION = 'user_location'


class ChatSession(models.Model):
    user_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    current_step = models.CharField(max_length=50, default=STEPS.WELCOME)
    payloads = ArrayField(models.TextField(null=True), default=list)
    last_save_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} started at @{self.created_at.replace(microsecond=0)}'
