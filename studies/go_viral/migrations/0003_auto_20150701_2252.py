# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('go_viral', '0002_datafile_subtype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datafile',
            options={'verbose_name': 'GoViral data file'},
        ),
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name': 'GoViral user data', 'verbose_name_plural': 'GoViral user data'},
        ),
    ]
