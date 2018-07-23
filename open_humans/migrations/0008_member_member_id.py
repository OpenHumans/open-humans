# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0007_member_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_id',
            field=models.CharField(max_length=8, blank=True),
            preserve_default=True,
        ),
    ]
