# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import open_humans.models


def add_member_ids(apps, schema_editor):
    Member = apps.get_model('open_humans', 'Member')
    for member in Member.objects.all():
        if not member.member_id:
            member.member_id = open_humans.models._mk_rand_member_id()
            member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('open_humans', '0007_member_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_id',
            field=models.CharField(blank=True, unique=False, max_length=8),
            preserve_default=True,
        ),
        migrations.RunPython(add_member_ids),
        migrations.AlterField(
            model_name='member',
            name='member_id',
            field=models.CharField(default=open_humans.models._mk_rand_member_id, unique=True, max_length=8),
            preserve_default=True,
        ),
    ]
