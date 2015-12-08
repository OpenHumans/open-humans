# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0002_staged_accesslog_removal'),
        ('data_import', '0004_datafileaccesslog'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RenameModel('PublicDataAccess', 'PublicDataFileAccess'),
        migrations.CreateModel(
            name='PublicDataAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_source', models.CharField(max_length=100)),
                ('is_public', models.BooleanField(default=False)),
                ('participant', models.ForeignKey(to='public_data.Participant')),
            ],
        ),
    ]
