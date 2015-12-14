# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0005_datafile_subtype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='subtype',
        ),
    ]
