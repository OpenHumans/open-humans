# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0002_auto_20150501_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdatafile',
            name='subtype',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
