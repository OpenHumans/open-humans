# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('go_viral', '0004_userdata_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='subtype',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
