# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-30 12:22
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0004_auto_20190330_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='steps_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name=models.TextField(null=True)),
        ),
    ]
