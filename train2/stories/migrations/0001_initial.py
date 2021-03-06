# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-01-14 20:40
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dump', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_saved_at', models.DateTimeField(auto_now=True)),
                ('checksum', models.CharField(db_index=True, max_length=100)),
            ],
        ),
    ]
