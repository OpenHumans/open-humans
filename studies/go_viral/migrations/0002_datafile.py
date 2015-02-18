# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0003_auto_20150206_0609'),
        ('go_viral', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=data_import.models.get_upload_path)),
                ('task', models.ForeignKey(related_name='datafile_go_viral', to='data_import.DataRetrievalTask')),
                ('user_data', models.ForeignKey(to='go_viral.UserData')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
