# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.models

sql = """UPDATE django_content_type
         SET name = 'user data',
             model = 'userdata'
         WHERE name = 'activity user' AND
               model = 'activityuser' AND
               app_label = 'twenty_three_and_me';
         UPDATE django_content_type
         SET name = 'data file',
             model = 'datafile'
         WHERE name = 'activity data file' AND
               model = 'activitydatafile' AND
               app_label = 'twenty_three_and_me';
         UPDATE django_content_type
         SET name = 'data retrieval task',
             model = 'dataretrievaltask'
         WHERE name = 'data extraction task' AND
               model = 'dataextractiontask' AND
               app_label = 'twenty_three_and_me';"""

reverse_sql = """UPDATE django_content_type
                 SET name = 'activity user',
                     model = 'activityuser'
                 WHERE name = 'user data' AND
                       model = 'userdata' AND
                       app_label = 'twenty_three_and_me';
                 UPDATE django_content_type
                 SET name = 'activity data file',
                     model = 'activitydatafile'
                 WHERE name = 'data file' AND
                       model = 'datafile' AND
                       app_label = 'twenty_three_and_me';
                 UPDATE django_content_type
                 SET name = 'data extraction task',
                     model = 'dataextractiontask'
                 WHERE name = 'data retrieval task' AND
                       model = 'dataretrievaltask' AND
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
            field=models.FileField(upload_to=common.models.get_upload_path),
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
