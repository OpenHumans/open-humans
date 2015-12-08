# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def copy_access_logs(apps, schema_editor):
    """
    Copying logs associated with public data files to logs for all files.
    """
    PublicDataAccessLog = apps.get_model('public_data', 'AccessLog')
    DataFileAccessLog = apps.get_model('data_import', 'DataFileAccessLog')
    for logitem in PublicDataAccessLog.objects.all():
        newlog = DataFileAccessLog(
            date=logitem.date,
            ip_address=logitem.ip_address,
            user=logitem.user,
            data_file_id=logitem.public_data_access.data_file_id,
            data_file_model=logitem.public_data_access.data_file_model)
        newlog.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_import', '0003_auto_20151120_0543'),
        ('public_data', '0001_squashed_0009_auto_20150325_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFileAccessLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('data_file_id', models.PositiveIntegerField()),
                ('data_file_model', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.RunPython(copy_access_logs,
                             reverse_code=migrations.RunPython.noop),
    ]
