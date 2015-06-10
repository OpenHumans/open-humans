# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0010_auto_20150602_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datarequest',
            name='study',
            field=models.ForeignKey(related_query_name=b'data_request', related_name='data_requests', to='studies.Study'),
        ),
    ]
