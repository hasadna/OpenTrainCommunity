# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-23 11:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0014_chatsession_platform'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatreport',
            name='attachments',
        ),
        migrations.AddField(
            model_name='chatreport',
            name='accept_payload_index',
            field=models.IntegerField(default=-1),
        ),
    ]
