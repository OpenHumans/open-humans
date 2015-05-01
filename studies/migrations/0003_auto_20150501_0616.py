# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0002_researcher_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('principal_investigator', models.CharField(max_length=128)),
                ('organization', models.CharField(max_length=128)),
                ('is_live', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='researcher',
            name='name',
            field=models.CharField(max_length=48),
        ),
        migrations.AddField(
            model_name='study',
            name='researchers',
            field=models.ForeignKey(to='studies.Researcher'),
        ),
    ]
