# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0001_squashed_0007_auto_20150306_2156'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datafile',
            options={'verbose_name': '23andMe data file'},
        ),
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name': '23andMe user data', 'verbose_name_plural': '23andMe user data'},
        ),
    ]
