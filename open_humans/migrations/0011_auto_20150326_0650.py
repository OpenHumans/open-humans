# -*- coding: utf-8 -*-

from django.db import models, migrations
import open_humans.models
import open_humans.storage


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0010_auto_20150311_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='profile_image',
            field=models.ImageField(storage=open_humans.storage.PublicStorage(), upload_to=open_humans.models.get_member_profile_image_upload_path, blank=True),
            preserve_default=True,
        ),
    ]
