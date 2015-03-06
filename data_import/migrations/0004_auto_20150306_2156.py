# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0003_auto_20150206_0609'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataretrievaltask',
            options={'ordering': ['-start_time']},
        ),
        migrations.AlterField(
            model_name='testdatafile',
            name='file',
            field=models.FileField(max_length=1024, upload_to=data_import.models.get_upload_path),
            preserve_default=True,
        ),
    ]
