# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20150913_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='max_booking_days',
            field=models.PositiveIntegerField(default=60, verbose_name='Buchungszeitraum'),
        ),
    ]
