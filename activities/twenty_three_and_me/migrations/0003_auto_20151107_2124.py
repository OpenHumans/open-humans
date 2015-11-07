# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0002_auto_20150701_2322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profileid',
            name='user_data',
        ),
        migrations.DeleteModel(
            name='ProfileId',
        ),
    ]
