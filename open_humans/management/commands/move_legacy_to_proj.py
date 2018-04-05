import datetime
import random
import string
import urlparse

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils import timezone

from oauth2_provider.models import Grant, RefreshToken
import requests

from data_import.models import DataFile
from open_humans.models import Member
from private_sharing.models import (
    DataRequestProject, DataRequestProjectMember, ProjectDataFile)
from public_data.models import PublicDataAccess


class Command(BaseCommand):
    """
    Transfer a legacy source to an OH-operated project.

    Creates a corresponding project membership, and modifies associated
    DataFile objects to be associated with this project.

    ID and slug of the target project are both requested in input to reduce
    the chance of accidentally transfering to an incorrect project.

    This function is written generically because it may be re-used in the
    future, but it needs to be tested with each app! self.ALLOWED_APPS reflects
    this; modify this only after testing.
    """

    ALLOWED_APPS = ['twenty_three_and_me']
    help = 'Transfer a legacy source to a project'

    def add_arguments(self, parser):
        parser.add_argument('--legacy', type=str,
                            help='label of legacy source to be transferred')
        parser.add_argument('--proj-id', type=str,
                            help='ID of project to transfer to')
        parser.add_argument('--proj-slug', type=str,
                            help='Slug of project to transfer to')
        parser.add_argument('--base-url', type=str,
                            help='Base URL to send OAuth2 request')
        parser.add_argument('--user', type=str,
                            help='Transfer just a specific user by username')
        parser.add_argument('--all-users', action='store_true',
                            help='Run for all users')

    def handle(self, *args, **options):
        self.base_url = options['base_url']
        proj_id = options['proj_id']
        proj_slug = options['proj_slug']
        legacy_source = options['legacy']
        username = options['user']
        all_users = options['all_users']

        if username and all_users:
            raise ValueError('Either specify a user or all-users, not both!')

        project = self._get_proj(
            proj_id=proj_id, proj_slug=proj_slug)
        legacy_config, legacy_files_by_uid = self._get_legacy(
            legacy_source=legacy_source)

        if username:
            uid_list = [Member.objects.get(user__username=username).user.id]
        elif all_users:
            uid_list = sorted(legacy_files_by_uid.keys())
        else:
            uid_list = []

        self._transfer_public_status(
            old_source=legacy_source, new_source=project.id_label)

        for uid in uid_list:
            project_member = self._create_projmember(project=project, uid=uid)
            user = project_member.member.user

            print('Transferring {}...'.format(user.username))

            if uid in legacy_files_by_uid:
                for df in legacy_files_by_uid[uid]:
                    df.source = project.id_label
                    df.save()
                    self._create_projdatafile(df, project_member)

            print('Transferred {}'.format(user.username))

    def _get_proj(self, proj_id, proj_slug):
        project = DataRequestProject.objects.get(id=proj_id)
        if proj_slug != project.slug:
            raise ValueError("Project ID ({}) and slug ({}) don't "
                             'match!'.format(proj_id, proj_slug))
        return project

    def _get_legacy(self, legacy_source):
        if legacy_source not in self.ALLOWED_APPS:
            raise ValueError('App label "{}" not in ALLOWED_APPS!'.format(
                legacy_source))

        legacy_config = apps.get_app_config(legacy_source)

        legacy_files = DataFile.objects.filter(source=legacy_source).current()
        legacy_files_by_uid = {k: [] for k in set([
            df.user.id for df in legacy_files])}
        for df in legacy_files:
            legacy_files_by_uid[df.user.id].append(df)

        return legacy_config, legacy_files_by_uid

    def _transfer_public_status(self, old_source, new_source):
        access_list = PublicDataAccess.objects.filter(data_source=old_source)
        for access in access_list:
            access.data_source = new_source
            access.save()

    def _create_projmember(self, project, uid):
        member = Member.objects.get(user__id=uid)
        project_member, _ = DataRequestProjectMember.objects.get_or_create(
            member=member,
            project=project)
        if project.type == 'oauth2':
            project_member.joined = True
            refresh_tokens = RefreshToken.objects.filter(
                user=project_member.member.user,
                application=project.oauth2datarequestproject.application)
            if not refresh_tokens:
                self._create_tokens(project=project, member=member)

        project_member.authorized = True
        project_member.revoked = False
        project_member.message_permission = project.request_message_permission
        project_member.username_shared = project.request_username_access
        project_member.sources_shared = project.request_sources_access
        project_member.all_sources_shared = project.all_sources_access
        project_member.save()

        return project_member

    def _create_projdatafile(self, df, proj_member):
        pdf = ProjectDataFile(
            completed=True,
            parent=df,
            direct_sharing_project=proj_member.project,
            user=proj_member.member.user,
            source=df.source,
            archived=df.archived,
            created=df.created,
            metadata=df.metadata,
            file=df.file)
        pdf.save()
        return pdf

    def _create_tokens(self, project, member):
        app = project.oauth2datarequestproject.application
        redirect_uri = app.redirect_uris.split()[0]
        code = ''.join(random.choice(string.ascii_letters + string.digits) for
                       _ in range(30))
        grant = Grant(user=member.user,
                      application=app,
                      expires=timezone.now() + datetime.timedelta(seconds=10),
                      code=code,
                      redirect_uri=redirect_uri)
        grant.save()
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code,
        }
        token_url = urlparse.urljoin(self.base_url, '/oauth2/token/')
        requests.post(
            token_url, data=data,
            auth=requests.auth.HTTPBasicAuth(app.client_id, app.client_secret))
