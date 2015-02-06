# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0002_dataretrievaltask_app_task_params'),
        ('american_gut', '0003_auto_20140922_1754'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=data_import.models.get_upload_path)),
                ('task', models.ForeignKey(related_name='datafile_american_gut', to='data_import.DataRetrievalTask')),
                ('user_data', models.ForeignKey(to='american_gut.UserData')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
