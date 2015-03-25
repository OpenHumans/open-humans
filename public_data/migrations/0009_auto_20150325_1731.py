# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0008_auto_20150227_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawalfeedback',
            name='feedback',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
