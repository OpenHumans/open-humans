# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import open_humans.models


def add_member_ids(apps, schema_editor):
    Member = apps.get_model('open_humans', 'Member')

    for member in Member.objects.all():
        if not member.member_id:
            member.member_id = open_humans.models.random_member_id()
            member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0007_member_name'),
    ]

    operations = [
        # add the field and allow empty and duplicate values
        migrations.AddField(
            model_name='member',
            name='member_id',
            field=models.CharField(blank=True, unique=False, max_length=8),
            preserve_default=True,
        ),
        # add member IDs for all members without them
        migrations.RunPython(add_member_ids),
        # alter the field to disallow blank and duplicate values
        migrations.AlterField(
            model_name='member',
            name='member_id',
            field=models.CharField(blank=False, unique=True),
            preserve_default=True,
        ),
    ]
