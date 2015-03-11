# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import open_humans.models


def add_member_ids(apps, *args):
    Member = apps.get_model('open_humans', 'Member')

    for member in Member.objects.all():
        if not member.member_id:
            member.member_id = open_humans.models.random_member_id()
            member.save()


class Migration(migrations.Migration):
    dependencies = [
        ('open_humans', '0008_member_member_id'),
    ]

    operations = [
        # add member IDs for all members without them
        migrations.RunPython(add_member_ids),
    ]
