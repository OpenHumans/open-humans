# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0001_squashed_0004_auto_20150306_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='testdatafile',
            name='subtype',
            field=models.CharField(default=b'', max_length=64),
        ),
        migrations.AddField(
            model_name='testdatafile',
            name='task',
            field=models.ForeignKey(related_name='datafile_test_data_file', blank=True, to='data_import.DataRetrievalTask', null=True),
        ),
    ]
