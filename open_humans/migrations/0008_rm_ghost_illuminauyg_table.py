# -*- coding: utf-8 -*-

from django.db import migrations

DROP_UNUSED_TABLES = """\
    DROP TABLE IF EXISTS illumina_uyg_userdata;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0007_blogpost'),
    ]

    operations = [
        migrations.RunSQL(DROP_UNUSED_TABLES),
    ]
