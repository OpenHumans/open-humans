# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataretrievaltask',
            name='app_task_params',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
