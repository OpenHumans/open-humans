# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import activities.twenty_three_and_me.models


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0003_auto_20151107_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='genome_file',
            field=models.FileField(max_length=1024, null=True, upload_to=activities.twenty_three_and_me.models.get_upload_path),
        ),
    ]
