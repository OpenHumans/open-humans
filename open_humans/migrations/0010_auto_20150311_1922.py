# -*- coding: utf-8 -*-

from django.db import models, migrations
import open_humans.models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0009_random_member_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='member_id',
            field=models.CharField(default=open_humans.models.random_member_id, unique=True, max_length=8),
            preserve_default=True,
        ),
    ]
