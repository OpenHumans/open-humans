# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0004_auto_20150126_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='member',
            field=common.fields.AutoOneToOneField(related_name='public_data_participant', to='open_humans.Member'),
            preserve_default=True,
        ),
    ]
