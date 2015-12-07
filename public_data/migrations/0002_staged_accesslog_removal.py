# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0001_squashed_0009_auto_20150325_1731'),
        ('data_import', '0004_datafileaccesslog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesslog',
            name='public_data_access',
        ),
        migrations.RemoveField(
            model_name='accesslog',
            name='user',
        ),
        migrations.DeleteModel(
            name='AccessLog',
        ),
    ]
