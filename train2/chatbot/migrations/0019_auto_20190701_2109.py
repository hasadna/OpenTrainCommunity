# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-01 18:09
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0018_remove_chatreport_accept_payload_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatreport',
            name='user_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
