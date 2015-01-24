# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('public_data', '0002_auto_20150123_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicDataStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_file_id', models.PositiveIntegerField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_file_model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
