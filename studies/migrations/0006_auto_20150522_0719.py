# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0005_study_website'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='study',
            name='researchers',
        ),
        migrations.AddField(
            model_name='study',
            name='researchers',
            field=models.ManyToManyField(to='studies.Researcher'),
        ),
    ]
