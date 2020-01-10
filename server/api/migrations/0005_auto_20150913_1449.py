# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def set_default_booking_unit(apps, schema_editor):
    Building = apps.get_model('api', 'Building')
    for building in Building.objects.all():
        building.booking_unit = 2
        building.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_building_booking_unit'),
    ]

    operations = [
        migrations.RunPython(set_default_booking_unit, set_default_booking_unit)
    ]
