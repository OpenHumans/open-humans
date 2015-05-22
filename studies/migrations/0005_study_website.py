# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0004_datarequirement'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='website',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
