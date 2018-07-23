# -*- coding: utf-8 -*-

from django.db import migrations
from django.conf import settings

sql = """UPDATE django_content_type
         SET model = 'member'
         WHERE model = 'profile' AND
               app_label = 'open_humans';"""

reverse_sql = """UPDATE django_content_type
                 SET model = 'profile'
                 WHERE model = 'member' AND
                       app_label = 'open_humans';"""


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('open_humans', '0004_auto_20150106_1828'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql)
    ]
