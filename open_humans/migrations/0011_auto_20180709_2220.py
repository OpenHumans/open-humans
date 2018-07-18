# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0010_auto_20180611_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='image_url',
            field=models.CharField(blank=True, max_length=2083),
        ),
    ]
