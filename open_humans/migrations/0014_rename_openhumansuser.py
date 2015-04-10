# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

sql = """UPDATE django_content_type
         SET model = 'user'
         WHERE model = 'openhumansuser' AND
               app_label = 'open_humans';"""

reverse_sql = """UPDATE django_content_type
                 SET model = 'openhumansuser'
                 WHERE model = 'user' AND
                       app_label = 'open_humans';"""


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('open_humans', '0013_auto_20150403_2323'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql)
    ]
