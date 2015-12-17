# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('go_viral', '0005_auto_20151120_0543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='subtype',
        ),
    ]
