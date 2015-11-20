# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0005_auto_20151008_2354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='subtype',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
