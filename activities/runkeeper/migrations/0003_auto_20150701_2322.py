# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('runkeeper', '0002_datafile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datafile',
            options={'verbose_name': 'RunKeeper data file'},
        ),
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name': 'RunKeeper user data', 'verbose_name_plural': 'RunKeeper user data'},
        ),
    ]
