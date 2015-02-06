# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0007_member_name'),
        ('public_data', '0005_auto_20150205_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithdrawalFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField()),
                ('member', models.OneToOneField(to='open_humans.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
