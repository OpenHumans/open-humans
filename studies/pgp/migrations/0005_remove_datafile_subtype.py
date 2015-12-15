# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgp', '0004_userdata_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='subtype',
        ),
    ]
