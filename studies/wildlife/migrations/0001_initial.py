# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import data_import.models
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_import', '0002_auto_20150501_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path)),
                ('subtype', models.CharField(default=b'wildlife', max_length=64)),
                ('task', models.ForeignKey(related_name='datafile_wildlife', to='data_import.DataRetrievalTask')),
            ],
            options={
                'verbose_name': 'Wildlife of Our Homes data file',
            },
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', jsonfield.fields.JSONField()),
                ('user', common.fields.AutoOneToOneField(related_name='wildlife', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Wildlife of Our Homes user data',
                'verbose_name_plural': 'Wildlife of Our Homes user data',
            },
        ),
        migrations.AddField(
            model_name='datafile',
            name='user_data',
            field=models.ForeignKey(to='wildlife.UserData'),
        ),
    ]
