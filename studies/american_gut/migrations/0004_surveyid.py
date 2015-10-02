# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0003_auto_20150701_2252'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyId',
            fields=[
                ('value', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('user_data', models.ForeignKey(related_name='survey_ids', to='american_gut.UserData')),
            ],
        ),
    ]
