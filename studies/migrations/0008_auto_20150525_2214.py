# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0007_auto_20150525_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 25, 22, 13, 52, 981561), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='study',
            name='slug',
            field=autoslug.fields.AutoSlugField(default='default-slug', editable=False, populate_from=b'title', unique=True),
            preserve_default=False,
        ),
    ]
