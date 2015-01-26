# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0001_initial'),
        ('twenty_three_and_me', '0002_auto_20150123_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='member',
            field=models.OneToOneField(related_name='public_data_participant', to='open_humans.Member'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicsharing23andme',
            name='data_file',
            field=common.fields.AutoOneToOneField(to='twenty_three_and_me.DataFile'),
            preserve_default=True,
        ),
    ]
