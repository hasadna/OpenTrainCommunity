# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stop_ids', django.contrib.postgres.fields.ArrayField(size=None, unique=True, base_field=models.IntegerField(), db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('stop_id', models.IntegerField(db_index=True)),
                ('stop_name', models.CharField(max_length=100)),
                ('is_skipped', models.BooleanField(default=False)),
                ('valid', models.BooleanField(default=False, db_index=True)),
                ('is_first', models.BooleanField(default=False)),
                ('is_last', models.BooleanField(default=False)),
                ('actual_arrival', models.DateTimeField(null=True, blank=True)),
                ('exp_arrival', models.DateTimeField(null=True, blank=True)),
                ('delay_arrival', models.FloatField(null=True, blank=True)),
                ('actual_departure', models.DateTimeField(null=True, blank=True)),
                ('exp_departure', models.DateTimeField(null=True, blank=True)),
                ('delay_departure', models.FloatField(null=True, blank=True)),
                ('data_file', models.CharField(max_length=100)),
                ('data_file_line', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('local_time_str', models.TextField(default=None)),
                ('route', models.ForeignKey(related_name='services', to='data.Route')),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.CharField(max_length=30, unique=True, serialize=False, primary_key=True, db_index=True)),
                ('valid', models.BooleanField(default=False)),
                ('trip_name', models.CharField(max_length=30, db_index=True)),
                ('train_num', models.IntegerField(db_index=True)),
                ('start_date', models.DateField(db_index=True)),
                ('route', models.ForeignKey(related_name='trips', to='data.Route')),
                ('service', models.ForeignKey(related_name='trips', to='data.Service', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='trip',
            field=models.ForeignKey(related_name='samples', blank=True, to='data.Trip', null=True),
        ),
    ]
