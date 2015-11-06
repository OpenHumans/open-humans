# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0001_squashed_0016_auto_20150410_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='seen_pgp_interstitial',
            field=models.BooleanField(default=False),
        ),
    ]
