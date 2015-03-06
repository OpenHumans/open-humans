# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('twenty_three_and_me', '0005_auto_20150205_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_id', models.CharField(max_length=16)),
                ('user_data', models.OneToOneField(to='twenty_three_and_me.UserData')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='user',
            field=common.fields.AutoOneToOneField(related_name='twenty_three_and_me', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
