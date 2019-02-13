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
        parser.add_argument('--start-date', type=str, help='stats as of this date')
        parser.add_argument('--end-date', type=str, help='stats up to this date')

    def handle(self, *args, **options):
        start_cutoff = arrow.get(options['start_date'])
        end_cutoff = arrow.get(options['end_date'])

        for date in arrow.Arrow.range('day', start_cutoff, end_cutoff):
            cutoff = date.datetime
            members = Member.objects.filter(user__date_joined__lte=cutoff).filter(
                user__is_active=True
            )
            members_with_data = members.annotate(
                datafiles_count=Count('user__datafiles')
            ).filter(datafiles_count__gte=1)
            projects_made = DataRequestProject.objects.filter(created__lte=cutoff)
            projects_approved = projects_made.filter(approved=True)

            data_connections = (
                DataRequestProjectMember.objects.exclude(project__approved=False)
                .exclude(joined=False)
                .filter(member__user__is_active=True)
                .exclude(authorized=False)
                .exclude(project__returned_data_description='')
                .filter(created__lte=cutoff)
            )

            proj_connections = (
                DataRequestProjectMember.objects.exclude(project__approved=False)
                .exclude(joined=False)
                .filter(member__user__is_active=True)
                .exclude(authorized=False)
                .filter(created__lte=cutoff)
            )

            """
            print("Members: {}".format(members.count()))
            print("Members with data: {}".format(
                members_with_data.count()))
            print("Data connections: {}".format(len(data_connections)))
            print("Project connections: {}".format(proj_connections.count()))
            print("Projects drafted: {}".format(projects_made.count()))
            print("Projects approved: {}".format(projects_approved.count()))
            """

            print(
                "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                    date.format('YYYY-MM-DD'),
                    members.count(),
                    members_with_data.count(),
                    len(data_connections),
                    proj_connections.count(),
                    projects_made.count(),
                    projects_approved.count(),
                )
            )
