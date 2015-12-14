# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0006_auto_20151120_0543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='subtype',
        ),
    ]
