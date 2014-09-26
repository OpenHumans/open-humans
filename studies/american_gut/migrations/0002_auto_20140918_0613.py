# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='user',
            field=common.fields.AutoOneToOneField(related_name=b'american_gut', to=settings.AUTH_USER_MODEL),
        ),
    ]
