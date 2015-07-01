# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0002_datafile_subtype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datafile',
            options={'verbose_name': 'American Gut data file'},
        ),
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name': 'American Gut user data', 'verbose_name_plural': 'American Gut user data'},
        ),
    ]
