# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-10 18:18
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0012_chatsession_attachments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatsession',
            name='attachments',
        ),
        migrations.AddField(
            model_name='chatreport',
            name='attachments',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
    ]
