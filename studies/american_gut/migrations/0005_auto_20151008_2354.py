# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('american_gut', '0004_surveyid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surveyid',
            name='user_data',
        ),
        migrations.AddField(
            model_name='userdata',
            name='data',
            field=jsonfield.fields.JSONField(default='{}'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='SurveyId',
        ),
    ]
