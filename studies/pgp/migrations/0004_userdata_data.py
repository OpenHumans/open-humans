# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pgp', '0003_auto_20150701_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=False,
        ),
    ]
