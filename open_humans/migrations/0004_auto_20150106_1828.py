# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import open_humans.models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0003_rename_profile_to_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='profile_image',
            field=models.ImageField(upload_to=open_humans.models.get_member_profile_image_upload_path, blank=True),
            preserve_default=True,
        ),
    ]
