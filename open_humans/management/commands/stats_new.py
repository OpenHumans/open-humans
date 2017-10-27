# -*- coding: utf-8 -*-

import arrow

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from termcolor import colored

from data_import.models import DataFile
from open_humans.models import Member
from private_sharing.models import DataRequestProject, DataRequestProjectMember
UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Statistics on the site'
    args = ''

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str,
                            help='stats as of this date')

    def handle(self, *args, **options):
        cutoff = arrow.get(options['date']).datetime

        members = Member.objects.filter(user__date_joined__lte=cutoff)
        members_with_data = members.annotate(
            datafiles_count=Count('user__datafiles')).filter(
            datafiles_count__gte=1)
        files = DataFile.objects.exclude(archived__lte=cutoff).filter(
            created__lte=cutoff)
        projects_made = DataRequestProject.objects.filter(created__lte=cutoff)
        projects_approved = projects_made.filter(approved=True)

        data_connections = set([(
            df['source'], df['user__username']) for
            df in DataFile.objects.exclude(
            archived__lte=cutoff).filter(
            created__lte=cutoff).values('user__username', 'source')])

        proj_connections = DataRequestProjectMember.objects.exclude(
            project__approved=False).exclude(joined=False).exclude(
            authorized=False).filter(created__lte=cutoff)

        print("Members: {}".format(members.count()))
        print("Members with any data connections: {}".format(
            members_with_data.count()))
        print("Data connections: {}".format(len(data_connections)))
        print("Project connections: {}".format(proj_connections.count()))
        print("Projects drafted: {}".format(projects_made.count()))
        print("Projects approved: {}".format(projects_approved.count()))
