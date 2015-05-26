# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('studies', '0008_auto_20150525_2214'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtype', models.TextField()),
                ('required', models.BooleanField(default=False)),
                ('data_file_model', models.ForeignKey(to='contenttypes.ContentType')),
                ('study', models.ForeignKey(to='studies.Study')),
            ],
        ),
        migrations.RemoveField(
            model_name='datarequirement',
            name='data_file_model',
        ),
        migrations.RemoveField(
            model_name='datarequirement',
            name='study',
        ),
        migrations.DeleteModel(
            name='DataRequirement',
        ),
        migrations.AddField(
            model_name='studygrant',
            name='data_requests',
            field=models.ManyToManyField(to='studies.DataRequest'),
        ),
    ]
