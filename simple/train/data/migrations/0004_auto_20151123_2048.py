# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20151104_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='is_planned',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='sample',
            name='is_stopped',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='sample',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]
