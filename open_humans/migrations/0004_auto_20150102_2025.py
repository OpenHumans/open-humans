# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0003_rename_profile_to_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='profile_image',
            field=models.ImageField(upload_to=b'member-images', blank=True),
            preserve_default=True,
        ),
    ]
