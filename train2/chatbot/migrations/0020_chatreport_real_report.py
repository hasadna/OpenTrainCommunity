# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-15 22:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0019_auto_20190701_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatreport',
            name='real_report',
            field=models.BooleanField(default=True),
        ),
    ]