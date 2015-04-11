# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    replaces = [(b'public_data', '0001_initial'), (b'public_data', '0002_auto_20150123_2126'), (b'public_data', '0003_publicdatastatus'), (b'public_data', '0004_auto_20150126_2009'), (b'public_data', '0005_auto_20150205_1918'), (b'public_data', '0006_withdrawalfeedback'), (b'public_data', '0007_accesslog'), (b'public_data', '0008_auto_20150227_2352'), (b'public_data', '0009_auto_20150325_1731')]

    dependencies = [
        ('open_humans', '0001_squashed_0016_auto_20150410_2301'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twenty_three_and_me', '0001_squashed_0007_auto_20150306_2156'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enrolled', models.BooleanField(default=False)),
                ('signature', models.CharField(max_length=70)),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('member', common.fields.AutoOneToOneField(related_name='public_data_participant', to='open_humans.Member')),
            ],
        ),
        migrations.CreateModel(
            name='PublicDataAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_file_id', models.PositiveIntegerField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_file_model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField()),
                ('withdrawal_date', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(to='open_humans.Member')),
            ],
        ),
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.RunSQL(
            sql="UPDATE django_content_type\n         SET model = 'publicdataaccess'\n         WHERE model = 'publicdatastatus' AND\n               app_label = 'public_data';",
            reverse_sql="UPDATE django_content_type\n                 SET model = 'publicdatastatus'\n                 WHERE model = 'publicdataaccess' AND\n                       app_label = 'public_data';",
        ),
        migrations.AddField(
            model_name='accesslog',
            name='public_data_access',
            field=models.ForeignKey(default=-1, to='public_data.PublicDataAccess'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='withdrawalfeedback',
            name='feedback',
            field=models.TextField(blank=True),
        ),
    ]
