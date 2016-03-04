# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-04 06:55
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_sharing', '0015_datarequestprojectmember_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datarequestprojectmember',
            name='message_permission',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='datarequestprojectmember',
            name='sources_shared',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='datarequestprojectmember',
            name='username_shared',
            field=models.BooleanField(default=False),
        ),
    ]
