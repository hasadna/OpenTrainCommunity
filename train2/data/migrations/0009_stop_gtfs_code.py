# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-30 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_sample_ignored_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='gtfs_code',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
