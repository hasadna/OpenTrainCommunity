# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_id', models.CharField(max_length=30, db_index=True)),
                ('train_num', models.IntegerField(db_index=True)),
                ('start_date', models.DateField(db_index=True)),
                ('index', models.IntegerField()),
                ('stop_id', models.IntegerField(db_index=True)),
                ('stop_name', models.CharField(max_length=100)),
                ('is_real_stop', models.BooleanField()),
                ('valid', models.BooleanField(db_index=True)),
                ('is_first', models.BooleanField()),
                ('is_last', models.BooleanField()),
                ('actual_arrival', models.DateTimeField(null=True, blank=True)),
                ('exp_arrival', models.DateTimeField(null=True, blank=True)),
                ('delay_arrival', models.FloatField(null=True, blank=True)),
                ('actual_departure', models.DateTimeField(null=True, blank=True)),
                ('exp_departure', models.DateTimeField(null=True, blank=True)),
                ('delay_departure', models.FloatField(null=True, blank=True)),
                ('data_file', models.CharField(max_length=100)),
                ('data_file_line', models.IntegerField()),
                ('data_file_link', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_id', models.CharField(unique=True, max_length=30, db_index=True)),
                ('train_num', models.IntegerField(db_index=True)),
                ('start_date', models.DateField(db_index=True)),
                ('valid', models.BooleanField(default=False)),
                ('stop_ids', djorm_pgarray.fields.IntegerArrayField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='parent_trip',
            field=models.ForeignKey(blank=True, to='data.Trip', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sample',
            unique_together=set([('trip_id', 'index')]),
        ),
    ]
