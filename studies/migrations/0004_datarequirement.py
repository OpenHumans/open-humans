# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('studies', '0003_auto_20150501_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataRequirement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtypes', models.TextField()),
                ('data_file_model', models.ForeignKey(to='contenttypes.ContentType')),
                ('study', models.ForeignKey(to='studies.Study')),
            ],
        ),
    ]
