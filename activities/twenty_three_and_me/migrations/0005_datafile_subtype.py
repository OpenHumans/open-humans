# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0004_userdata_genome_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='subtype',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
