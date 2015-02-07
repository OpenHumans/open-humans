# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0006_withdrawalfeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawalfeedback',
            name='withdrawal_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 7, 4, 24, 34, 615561), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='withdrawalfeedback',
            name='member',
            field=models.ForeignKey(to='open_humans.Member'),
            preserve_default=True,
        ),
    ]
