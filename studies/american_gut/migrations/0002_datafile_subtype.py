# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0001_squashed_0005_auto_20150306_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='subtype',
            field=models.CharField(default=b'microbiome-16S-and-surveys', max_length=64),
        ),
    ]
