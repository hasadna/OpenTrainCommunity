# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-18 20:04
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_auto_20190318_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatsession',
            name='payloads',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(null=True), default=list, size=None),
        ),
    ]