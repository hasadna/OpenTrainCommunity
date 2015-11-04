# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20151025_2033'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='sample',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='trip',
            options={'ordering': ['route_id', 'start_date', 'x_hour_local', 'id']},
        ),
    ]
