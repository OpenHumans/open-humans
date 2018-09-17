# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from oauth2_provider.models import RefreshToken
from private_sharing.models import DataRequestProject, DataRequestProjectMember


class Command(BaseCommand):
    help = 'Get refresh tokens'
    args = ''

    def add_arguments(self, parser):
        parser.add_argument('--proj-id', type=str,
                            help='ID of project to transfer to')

    def handle(self, *args, **options):
        drp = DataRequestProject.objects.get(id=options['proj_id'])
        app = drp.oauth2datarequestproject.application

        refresh_tokens = {rt.user.id: rt for rt in
                          RefreshToken.objects.filter(application=app)}
        drpms = {drpm.member.user.id: drpm for drpm in
                 DataRequestProjectMember.objects.filter(project=drp)}

        auth_refresh_tokens = {}

        for uid in sorted(drpms.keys()):
            print('{},{}'.format(drpms[uid].project_member_id,
                                 refresh_tokens[uid].token))
