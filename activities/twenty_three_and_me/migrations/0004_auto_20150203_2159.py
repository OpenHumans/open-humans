# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0001_initial'),
        ('twenty_three_and_me', '0003_auto_20150203_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataretrievaltask',
            name='data_file',
        ),
        migrations.DeleteModel(
            name='DataRetrievalTask',
        ),
        migrations.AddField(
            model_name='datafile',
            name='task',
            field=models.ForeignKey(default=1, to='data_import.DataRetrievalTask'),
            preserve_default=False,
        ),
    ]
