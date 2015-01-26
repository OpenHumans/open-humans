# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0005_rename_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='allow_user_messages',
            field=models.BooleanField(default=False, verbose_name=b'Allow members to contact me'),
            preserve_default=True,
        ),
    ]
