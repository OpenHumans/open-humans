# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import data_import.models
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=data_import.models.get_upload_path)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', common.fields.AutoOneToOneField(related_name=b'23andme', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataExtractionTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'Completed successfully'), (1, b'Submitted'), (2, b'Failed')])),
                ('start_time', models.DateTimeField(default=datetime.datetime.now)),
                ('complete_time', models.DateTimeField(null=True)),
                ('data_file', models.OneToOneField(null=True, to='twenty_three_and_me.ActivityDataFile')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='activitydatafile',
            name='study_user',
            field=models.ForeignKey(to='twenty_three_and_me.ActivityUser'),
            preserve_default=True,
        ),
    ]
