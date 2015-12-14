# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0012_auto_20151002_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datarequest',
            name='subtype',
        ),
    ]
