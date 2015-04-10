# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data_import.models

sql = """UPDATE django_content_type
         SET model = 'userdata'
         WHERE model = 'activityuser' AND
               app_label = 'twenty_three_and_me';
         UPDATE django_content_type
         SET model = 'datafile'
         WHERE model = 'activitydatafile' AND
               app_label = 'twenty_three_and_me';
         UPDATE django_content_type
         SET model = 'dataretrievaltask'
         WHERE model = 'dataextractiontask' AND
               app_label = 'twenty_three_and_me';"""

reverse_sql = """UPDATE django_content_type
                 SET model = 'activityuser'
                 WHERE model = 'userdata' AND
                       app_label = 'twenty_three_and_me';
                 UPDATE django_content_type
                 SET model = 'activitydatafile'
                 WHERE model = 'datafile' AND
                       app_label = 'twenty_three_and_me';
                 UPDATE django_content_type
                 SET model = 'dataextractiontask'
                 WHERE model = 'dataretrievaltask' AND
                       app_label = 'twenty_three_and_me';"""


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ActivityDataFile',
            new_name='DataFile',
        ),
        migrations.RenameModel(
            old_name='DataExtractionTask',
            new_name='DataRetrievalTask',
        ),
        migrations.RenameModel(
            old_name='ActivityUser',
            new_name='UserData',
        ),
        migrations.RenameField(
            model_name='datafile',
            old_name='study_user',
            new_name='user_data',
        ),
        migrations.AlterField(
            model_name='datafile',
            name='user_data',
            field=models.ForeignKey(to='twenty_three_and_me.UserData'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(upload_to=data_import.models.get_upload_path),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dataretrievaltask',
            name='data_file',
            field=models.OneToOneField(null=True, to='twenty_three_and_me.DataFile'),
            preserve_default=True,
        ),
        migrations.RunSQL(sql, reverse_sql),
    ]
