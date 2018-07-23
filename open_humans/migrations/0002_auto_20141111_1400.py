# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='allow_user_messages',
            field=models.BooleanField(default=True, verbose_name='Allow members to contact me'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='newsletter',
            field=models.BooleanField(default=True, verbose_name='Receive Open Humans news and updates'),
            preserve_default=True,
        ),
    ]
