# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0001_squashed_0016_auto_20150410_2301'),
        ('studies', '0006_auto_20150522_0719'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyGrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('revoked', models.DateTimeField(null=True)),
                ('member', models.ForeignKey(to='open_humans.Member')),
                ('study', models.ForeignKey(to='studies.Study')),
            ],
        ),
        migrations.RenameField(
            model_name='datarequirement',
            old_name='subtypes',
            new_name='subtype',
        ),
    ]
