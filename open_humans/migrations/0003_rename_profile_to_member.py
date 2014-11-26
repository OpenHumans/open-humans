# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('open_humans', '0002_auto_20141111_1400'),
    ]

    operations = [
        migrations.RenameModel('Profile', 'Member')
    ]
