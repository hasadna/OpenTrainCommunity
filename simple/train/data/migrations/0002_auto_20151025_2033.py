# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='x_hour_local',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='x_week_day_local',
            field=models.IntegerField(null=True),
        ),
    ]
