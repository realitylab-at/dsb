# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20150913_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='max_content',
            field=models.PositiveIntegerField(default=20, verbose_name='Max. dargestellte Eintr\xe4ge vom Typ Suche & Biete'),
        ),
    ]
