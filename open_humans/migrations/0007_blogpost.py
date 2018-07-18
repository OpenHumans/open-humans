# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0006_userevent_event_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rss_id', models.CharField(max_length=120, unique=True)),
                ('title', models.CharField(blank=True, max_length=120)),
                ('summary_long', models.TextField(blank=True)),
                ('summary_short', models.TextField(blank=True)),
                ('image_url', models.CharField(blank=True, max_length=120)),
                ('published', models.DateTimeField()),
            ],
        ),
    ]
