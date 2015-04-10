# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2_provider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='skip_authorization',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='user',
            field=models.ForeignKey(related_name='oauth2_provider_application', to=settings.AUTH_USER_MODEL),
        ),
    ]
