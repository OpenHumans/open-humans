# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0002_auto_20140918_0613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='barcode',
            name='id',
        ),
        migrations.AlterField(
            model_name='barcode',
            name='value',
            field=models.CharField(max_length=64, serialize=False, primary_key=True),
        ),
    ]
