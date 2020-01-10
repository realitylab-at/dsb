# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20150913_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='booking_unit',
            field=models.PositiveIntegerField(default=1, verbose_name='Buchungseinheit'),
        ),
    ]
