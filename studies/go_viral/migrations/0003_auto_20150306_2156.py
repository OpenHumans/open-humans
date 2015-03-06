# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('go_viral', '0002_datafile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path),
            preserve_default=True,
        ),
    ]
