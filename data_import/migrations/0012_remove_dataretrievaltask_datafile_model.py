# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-09 05:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0011_dataretrievaltask_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataretrievaltask',
            name='datafile_model',
        ),
    ]