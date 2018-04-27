# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from social.apps.django_app.default.models import UserSocialAuth

from oauth2_provider.models import RefreshToken
from private_sharing.models import DataRequestProject, DataRequestProjectMember


UserSocialAuth.objects.filter(provider='withings')[0].extra_data
UserSocialAuth.objects.filter(provider='withings')[0].user

class Command(BaseCommand):
    help = 'Get refresh tokens'
    args = ''

    def add_arguments(self, parser):
        parser.add_argument('--proj-id', type=str,
                            help='ID of project to transfer to')
        parser.add_argument('--social', type=str, default='',
                            help='(optional) String ID for social auth')

    def handle(self, *args, **options):
        drp = DataRequestProject.objects.get(id=options['proj_id'])
        app = drp.oauth2datarequestproject.application

        refresh_tokens = {rt.user.id: rt for rt in
                          RefreshToken.objects.filter(application=app)}
        drpms = {drpm.member.user.id: drpm for drpm in
                 DataRequestProjectMember.objects.filter(project=drp)}

        auth_refresh_tokens = {}
        if options['social']:
            usas = UserSocialAuth.objects.filter(provider=options['social'])
            auth_refresh_tokens = {usa.user.id: usa.extra_data['refresh_token']
                                   for usa in usas}

        for uid in sorted(drpms.keys()):
            if options['social']:
                print('{},{},{}'.format(drpms[uid].project_member_id,
                                        refresh_tokens[uid].token,
                                        auth_refresh_tokens[uid]))
            else:
                print('{},{}'.format(drpms[uid].project_member_id,
                                     refresh_tokens[uid].token))
