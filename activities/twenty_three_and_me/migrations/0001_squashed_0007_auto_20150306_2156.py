# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import data_import.models
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    replaces = [(b'twenty_three_and_me', '0001_initial'), (b'twenty_three_and_me', '0002_auto_20150123_2126'), (b'twenty_three_and_me', '0003_auto_20150203_1620'), (b'twenty_three_and_me', '0004_auto_20150203_2159'), (b'twenty_three_and_me', '0005_auto_20150205_1918'), (b'twenty_three_and_me', '0006_auto_20150303_1613'), (b'twenty_three_and_me', '0007_auto_20150306_2156')]

    dependencies = [
        ('data_import', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', common.fields.AutoOneToOneField(related_name=b'23andme', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=data_import.models.get_upload_path)),
                ('user_data', models.ForeignKey(to='twenty_three_and_me.UserData')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(upload_to=data_import.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='datafile',
            name='task',
            field=models.ForeignKey(related_name='datafile_23andme', to='data_import.DataRetrievalTask'),
        ),
        migrations.CreateModel(
            name='ProfileId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_id', models.CharField(max_length=16)),
                ('user_data', models.OneToOneField(to='twenty_three_and_me.UserData')),
            ],
        ),
        migrations.AlterField(
            model_name='userdata',
            name='user',
            field=common.fields.AutoOneToOneField(related_name='twenty_three_and_me', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path),
        ),
    ]
