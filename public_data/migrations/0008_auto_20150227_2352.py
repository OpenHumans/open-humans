# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

sql = """UPDATE django_content_type
         SET name = 'public data access',
             model = 'publicdataaccess'
         WHERE name = 'public data status' AND
               model = 'publicdatastatus' AND
               app_label = 'public_data';"""

reverse_sql = """UPDATE django_content_type
                 SET name = 'public data status',
                     model = 'publicdatastatus'
                 WHERE name = 'public data access' AND
                       model = 'publicdataaccess' AND
                       app_label = 'public_data';"""


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('public_data', '0007_accesslog'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PublicDataStatus',
            new_name='PublicDataAccess'
        ),
        migrations.RunSQL(sql, reverse_sql),
        migrations.RemoveField(
            model_name='accesslog',
            name='data_file_id',
        ),
        migrations.RemoveField(
            model_name='accesslog',
            name='data_file_model',
        ),
        migrations.AddField(
            model_name='accesslog',
            name='public_data_access',
            field=models.ForeignKey(default=-1, to='public_data.PublicDataAccess'),
            preserve_default=False,
        ),
    ]
