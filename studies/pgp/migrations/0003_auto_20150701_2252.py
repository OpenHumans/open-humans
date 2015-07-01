# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pgp', '0002_datafile_subtype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datafile',
            options={'verbose_name': 'PGP data file'},
        ),
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name': 'PGP user data', 'verbose_name_plural': 'PGP user data'},
        ),
    ]
