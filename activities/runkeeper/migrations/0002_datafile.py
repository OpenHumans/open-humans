# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0002_auto_20150501_0616'),
        ('runkeeper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path)),
                ('task', models.ForeignKey(related_name='datafile_runkeeper', to='data_import.DataRetrievalTask')),
                ('user_data', models.ForeignKey(to='runkeeper.UserData')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
