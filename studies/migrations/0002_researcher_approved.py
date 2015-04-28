# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='approved',
            field=models.NullBooleanField(),
        ),
    ]
