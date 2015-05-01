# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pgp', '0001_squashed_0003_auto_20150306_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='subtype',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
