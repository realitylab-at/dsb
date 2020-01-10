# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20150908_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='position',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='bookable',
            name='position',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
        ),
    ]
