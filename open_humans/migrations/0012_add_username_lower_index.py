# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

forward_sql = """CREATE UNIQUE INDEX auth_user_username_lower
                 ON auth_user (LOWER(username));"""

reverse_sql = """DROP INDEX auth_user_username_lower;"""


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0011_auto_20150326_0650'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql)
    ]
