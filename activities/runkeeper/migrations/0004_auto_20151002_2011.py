# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('runkeeper', '0003_auto_20150701_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='user_data',
            field=models.ForeignKey(related_name='datafiles', to='runkeeper.UserData'),
        ),
    ]
