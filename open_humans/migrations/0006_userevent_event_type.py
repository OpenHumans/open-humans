# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0005_userevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='userevent',
            name='event_type',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
