# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import data_import.models
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    replaces = [(b'data_import', '0001_initial'), (b'data_import', '0002_dataretrievaltask_app_task_params'), (b'data_import', '0003_auto_20150206_0609'), (b'data_import', '0004_auto_20150306_2156')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataRetrievalTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'Completed successfully'), (1, b'Submitted'), (2, b'Failed'), (3, b'Queued'), (4, b'Initiated'), (5, b'Postponed')])),
                ('start_time', models.DateTimeField(default=datetime.datetime.now)),
                ('complete_time', models.DateTimeField(null=True)),
                ('datafile_model', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('app_task_params', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='TestDataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=data_import.models.get_upload_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestUserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', common.fields.AutoOneToOneField(related_name='test_user_data', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='testdatafile',
            name='user_data',
            field=models.ForeignKey(to='data_import.TestUserData'),
        ),
        migrations.AlterModelOptions(
            name='dataretrievaltask',
            options={'ordering': ['-start_time']},
        ),
        migrations.AlterField(
            model_name='testdatafile',
            name='file',
            field=models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path),
        ),
    ]
