# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-30 10:49
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations import RunPython


def copy_to_list(apps, schema_editor):
    Stop = apps.get_model('data', 'Stop')
    for s in Stop.objects.all():
        s.hebrew_list = s.hebrews
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_stop_hebrew_list'),
    ]

    operations = [
        RunPython(copy_to_list, RunPython.noop)
    ]
