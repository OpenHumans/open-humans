# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0011_auto_20150610_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygrant',
            name='member',
            field=models.ForeignKey(related_name='study_grants', to='open_humans.Member'),
        ),
    ]
