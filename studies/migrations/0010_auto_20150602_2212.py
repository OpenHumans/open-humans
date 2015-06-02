# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0009_auto_20150526_1928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='study',
            options={'verbose_name_plural': 'studies'},
        ),
        migrations.RenameField(
            model_name='study',
            old_name='description',
            new_name='long_description',
        ),
        migrations.AddField(
            model_name='study',
            name='short_description',
            field=models.CharField(default='', max_length=140),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='study',
            name='researchers',
            field=models.ManyToManyField(to='studies.Researcher', blank=True),
        ),
    ]
