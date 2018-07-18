# -*- coding: utf-8 -*-

from django.db import migrations, models
import open_humans.models
import open_humans.storage


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0009_grantproject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantproject',
            name='photo',
            field=models.ImageField(blank=True, max_length=1024, storage=open_humans.storage.PublicStorage(), upload_to=open_humans.models.get_grant_project_image_upload_path),
        ),
    ]
