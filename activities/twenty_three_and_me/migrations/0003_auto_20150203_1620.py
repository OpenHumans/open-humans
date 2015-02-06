# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0002_auto_20150123_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataretrievaltask',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'Completed successfully'), (1, b'Submitted'), (2, b'Failed'), (3, b'Queued'), (4, b'Initiated'), (5, b'Postponed')]),
            preserve_default=True,
        ),
    ]
