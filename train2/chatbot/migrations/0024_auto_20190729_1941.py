# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-29 16:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0023_auto_20190729_1930'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatreporttrip',
            old_name='trip_id',
            new_name='gtfs_trip_id',
        ),
    ]
