# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import common.fields
import data_import.models


class Migration(migrations.Migration):

    replaces = [(b'american_gut', '0001_initial'), (b'american_gut', '0002_auto_20140918_0613'), (b'american_gut', '0003_auto_20140922_1754'), (b'american_gut', '0004_datafile'), (b'american_gut', '0005_auto_20150306_2156')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_import', '0001_squashed_0004_auto_20150306_2156'),
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', common.fields.AutoOneToOneField(related_name=b'american_gut', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='barcode',
            name='user_data',
            field=models.ForeignKey(related_name=b'barcodes', to='american_gut.UserData'),
        ),
        migrations.RemoveField(
            model_name='barcode',
            name='id',
        ),
        migrations.AlterField(
            model_name='barcode',
            name='value',
            field=models.CharField(max_length=64, serialize=False, primary_key=True),
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path)),
                ('task', models.ForeignKey(related_name='datafile_american_gut', to='data_import.DataRetrievalTask')),
                ('user_data', models.ForeignKey(to='american_gut.UserData')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
