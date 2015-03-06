# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0006_auto_20150303_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path),
            preserve_default=True,
        ),
    ]
