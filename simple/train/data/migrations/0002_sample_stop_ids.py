# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='stop_ids',
            field=djorm_pgarray.fields.IntegerArrayField(db_index=True),
            preserve_default=True,
        ),
    ]
