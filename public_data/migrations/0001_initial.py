# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0006_auto_20150123_2121'),
        ('twenty_three_and_me', '0002_auto_20150123_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enrolled', models.BooleanField(default=False)),
                ('signature', models.CharField(max_length=70)),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('member', models.OneToOneField(to='open_humans.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublicSharing23AndMe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_public', models.BooleanField(default=False)),
                ('data_file', common.fields.AutoOneToOneField(to='twenty_three_and_me.DataFile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
