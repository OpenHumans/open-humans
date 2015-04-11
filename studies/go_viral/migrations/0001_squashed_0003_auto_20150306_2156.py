# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import common.fields
import data_import.models


class Migration(migrations.Migration):

    replaces = [(b'go_viral', '0001_initial'), (b'go_viral', '0002_datafile'), (b'go_viral', '0003_auto_20150306_2156')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_import', '0003_auto_20150206_0609'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoViralId',
            fields=[
                ('value', models.CharField(max_length=64, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', common.fields.AutoOneToOneField(related_name='go_viral', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='goviralid',
            name='user_data',
            field=models.ForeignKey(related_name='go_viral_ids', to='go_viral.UserData'),
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path)),
                ('task', models.ForeignKey(related_name='datafile_go_viral', to='data_import.DataRetrievalTask')),
                ('user_data', models.ForeignKey(to='go_viral.UserData')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
