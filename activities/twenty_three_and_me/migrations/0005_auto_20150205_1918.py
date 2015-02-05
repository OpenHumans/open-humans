# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0004_auto_20150203_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='task',
            field=models.ForeignKey(related_name='datafile_23andme', to='data_import.DataRetrievalTask'),
            preserve_default=True,
        ),
    ]
