# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-06-11 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0005_remove_datafile_is_latest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='archived',
        ),
    ]
