# -*- coding: utf-8 -*-

from django.db import migrations, models
import open_humans.models
import open_humans.storage


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0008_rm_ghost_illuminauyg_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('grant_date', models.DateField(null=True)),
                ('status', models.CharField(max_length=120)),
                ('github', models.TextField(blank=True)),
                ('grantee_name', models.CharField(max_length=255)),
                ('photo', models.ImageField(blank=True, max_length=1024, storage=open_humans.storage.PublicStorage(), upload_to=open_humans.models.get_member_profile_image_upload_path)),
                ('blog_url', models.TextField()),
                ('project_desc', models.TextField()),
            ],
        ),
    ]
