# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0003_publicdatastatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publicsharing23andme',
            name='data_file',
        ),
        migrations.DeleteModel(
            name='PublicSharing23AndMe',
        ),
    ]
